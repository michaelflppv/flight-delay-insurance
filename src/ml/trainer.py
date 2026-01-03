"""
Model training for flight delay prediction
"""

import logging
import numpy as np
import pandas as pd
import joblib
import gc
import warnings
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    accuracy_score, mean_absolute_error, mean_squared_error,
    r2_score, f1_score
)
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

from src.config import Config

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Train flight delay prediction models"""

    def __init__(self):
        """Initialize trainer with configuration"""
        self.config = Config()
        self.config.ensure_directories()

        # Data containers
        self.X_class_train = None
        self.X_class_val = None
        self.X_class_test = None
        self.y_class_train = None
        self.y_class_val = None
        self.y_class_test = None
        self.X_reg_train = None
        self.X_reg_val = None
        self.X_reg_test = None
        self.y_reg_train = None
        self.y_reg_val = None
        self.y_reg_test = None

        # Models
        self.model_class = None
        self.model_reg = None

        logger.info("ModelTrainer initialized")

    def load_and_prepare_data(self):
        """Load and prepare training data"""
        logger.info(f"Loading data from {self.config.FLIGHT_DATA_PATH}")

        # Load data
        selected_columns = [
            'ARR_DELAY', 'AIRLINE_CODE', 'ORIGIN', 'DEST',  # Airport codes, not cities!
            'CRS_DEP_TIME', 'FL_DATE', 'DISTANCE', 'CANCELLED', 'DIVERTED'
        ]

        try:
            df = pd.read_csv(self.config.FLIGHT_DATA_PATH, usecols=selected_columns)
            logger.info(f"Data loaded successfully. Shape: {df.shape}")
        except FileNotFoundError:
            logger.error(f"Data file not found at {self.config.FLIGHT_DATA_PATH}")
            logger.error("Please run 'make download-data' first")
            raise

        # Remove duplicates
        item0 = df.shape[0]
        df = df.drop_duplicates()
        item1 = df.shape[0]
        logger.info(f"Removed {item0 - item1} duplicates")
        gc.collect()

        # Feature engineering
        df['FL_DATE'] = pd.to_datetime(df['FL_DATE'])
        df['Month'] = df['FL_DATE'].dt.month  # 1-12 numeric
        df['Weekday'] = df['FL_DATE'].dt.dayofweek  # 0-6 numeric
        df['Quarter'] = df['FL_DATE'].dt.quarter
        df['Planned_departure_hour'] = df['CRS_DEP_TIME'] // 100

        # Cyclical encoding for temporal features (captures wraparound)
        df['Month_sin'] = np.sin(2 * np.pi * df['Month'] / 12)
        df['Month_cos'] = np.cos(2 * np.pi * df['Month'] / 12)
        df['Hour_sin'] = np.sin(2 * np.pi * df['Planned_departure_hour'] / 24)
        df['Hour_cos'] = np.cos(2 * np.pi * df['Planned_departure_hour'] / 24)
        df['Weekday_sin'] = np.sin(2 * np.pi * df['Weekday'] / 7)
        df['Weekday_cos'] = np.cos(2 * np.pi * df['Weekday'] / 7)

        # Select columns
        selected_cols = [
            'ARR_DELAY', 'AIRLINE_CODE', 'ORIGIN', 'DEST', 'DISTANCE',
            'CANCELLED', 'DIVERTED', 'Planned_departure_hour', 'Quarter',
            'Month_sin', 'Month_cos', 'Hour_sin', 'Hour_cos', 'Weekday_sin', 'Weekday_cos'
        ]
        df = df[selected_cols]

        # Filter cancelled/diverted flights BEFORE training
        logger.info(f"Before filtering - Shape: {df.shape}")
        df = df[df['CANCELLED'] == 0]
        df = df[df['DIVERTED'] == 0]
        df = df.drop(['CANCELLED', 'DIVERTED'], axis=1)
        logger.info(f"After filtering cancelled/diverted: {df.shape}")

        # Remove rows with missing arrival delay (instead of fillna(0))
        df = df.dropna(subset=['ARR_DELAY'])
        logger.info(f"After removing missing ARR_DELAY: {df.shape}")

        # Create classification dataset
        df['DELAYED'] = df['ARR_DELAY'] > 0
        X_class = df.drop(['DELAYED', 'ARR_DELAY'], axis=1)
        y_class = df['DELAYED'].values.reshape(-1,)

        # Create regression dataset (only delayed flights)
        X_reg = df[df['ARR_DELAY'] > 0].drop(['DELAYED', 'ARR_DELAY'], axis=1)
        y_reg = df[df['ARR_DELAY'] > 0]['ARR_DELAY'].values.reshape(-1,)

        # Get categorical columns
        cat_cols = df.select_dtypes(include=['object']).columns
        cat_cols = [c for c in cat_cols if c in X_class.columns]

        # One-hot encoding
        X_class = pd.get_dummies(X_class, columns=cat_cols)
        X_reg = pd.get_dummies(X_reg, columns=cat_cols)

        # Split data: 80% train, 10% validation, 10% test
        # First split: 80/20
        X_temp, self.X_class_test, y_temp, self.y_class_test = train_test_split(
            X_class, y_class,
            test_size=0.20,
            random_state=self.config.RANDOM_STATE,
            stratify=y_class
        )

        # Second split: 80/10/10 of total (split the temp 80% into 70/10)
        self.X_class_train, self.X_class_val, self.y_class_train, self.y_class_val = train_test_split(
            X_temp, y_temp,
            test_size=0.125,  # 0.125 * 0.80 = 0.10 of total
            random_state=self.config.RANDOM_STATE,
            stratify=y_temp
        )

        logger.info(f"Classification - Train: {self.X_class_train.shape}, "
                   f"Val: {self.X_class_val.shape}, Test: {self.X_class_test.shape}")

        # Same split strategy for regression
        X_reg_temp, self.X_reg_test, y_reg_temp, self.y_reg_test = train_test_split(
            X_reg, y_reg,
            test_size=0.20,
            random_state=self.config.RANDOM_STATE
        )

        self.X_reg_train, self.X_reg_val, self.y_reg_train, self.y_reg_val = train_test_split(
            X_reg_temp, y_reg_temp,
            test_size=0.125,
            random_state=self.config.RANDOM_STATE
        )

        logger.info(f"Regression - Train: {self.X_reg_train.shape}, "
                   f"Val: {self.X_reg_val.shape}, Test: {self.X_reg_test.shape}")

        # Clean up
        del df
        gc.collect()

    def train_classifier(self):
        """Train the delay classification model"""
        logger.info("Training classification model...")

        # Compute class weights
        classes = np.unique(self.y_class_train)
        weights = compute_class_weight(
            class_weight='balanced',
            classes=classes,
            y=self.y_class_train
        )
        class_weights = dict(zip(classes, weights))
        logger.info(f"Class weights: {class_weights}")

        # Train model
        self.model_class = RandomForestClassifier(
            n_estimators=self.config.N_ESTIMATORS,  # 200
            max_depth=self.config.MAX_DEPTH,  # 20 (prevent overfitting)
            min_samples_split=self.config.MIN_SAMPLES_SPLIT,  # 100
            min_samples_leaf=self.config.MIN_SAMPLES_LEAF,  # 50
            max_features=self.config.MAX_FEATURES,  # 'sqrt'
            class_weight=class_weights,
            random_state=self.config.RANDOM_STATE,
            verbose=2,
            n_jobs=self.config.N_JOBS,
            oob_score=True  # Free validation metric
        )
        self.model_class.fit(self.X_class_train, self.y_class_train)
        logger.info("Classification model training completed")

        # Evaluate
        self._evaluate_classifier(class_weights)

    def _evaluate_classifier(self, class_weights):
        """Comprehensive classifier evaluation"""

        # Predictions on train/val/test
        y_train_pred_proba = self.model_class.predict_proba(self.X_class_train)[:, 1]
        y_val_pred_proba = self.model_class.predict_proba(self.X_class_val)[:, 1]
        y_test_pred_proba = self.model_class.predict_proba(self.X_class_test)[:, 1]

        # ROC AUC
        roc_auc_train = roc_auc_score(self.y_class_train, y_train_pred_proba)
        roc_auc_val = roc_auc_score(self.y_class_val, y_val_pred_proba)
        roc_auc_test = roc_auc_score(self.y_class_test, y_test_pred_proba)

        logger.info(f"ROC AUC - Train: {roc_auc_train:.4f}, Val: {roc_auc_val:.4f}, Test: {roc_auc_test:.4f}")

        # Check for overfitting
        if roc_auc_train - roc_auc_val > 0.05:
            logger.warning("Possible overfitting detected (train-val gap > 0.05)")

        # Binary predictions
        y_val_pred = self.model_class.predict(self.X_class_val)
        y_test_pred = self.model_class.predict(self.X_class_test)

        # Accuracy and F1
        val_accuracy = accuracy_score(self.y_class_val, y_val_pred)
        test_accuracy = accuracy_score(self.y_class_test, y_test_pred)
        val_f1 = f1_score(self.y_class_val, y_val_pred)
        test_f1 = f1_score(self.y_class_test, y_test_pred)

        logger.info(f"Accuracy - Val: {val_accuracy:.4f}, Test: {test_accuracy:.4f}")
        logger.info(f"F1 Score - Val: {val_f1:.4f}, Test: {test_f1:.4f}")

        # OOB Score
        if hasattr(self.model_class, 'oob_score_'):
            logger.info(f"OOB Score: {self.model_class.oob_score_:.4f}")

        # Feature importance
        self._log_feature_importance('classifier')

        # Detailed metrics
        logger.info("\nClassification Report (Validation):")
        print(classification_report(self.y_class_val, y_val_pred))

        logger.info("\nConfusion Matrix (Validation):")
        print(confusion_matrix(self.y_class_val, y_val_pred))

    def train_regressor(self):
        """Train the delay duration regression model"""
        logger.info("Training regression model...")

        self.model_reg = RandomForestRegressor(
            n_estimators=self.config.N_ESTIMATORS,  # 200
            max_depth=self.config.MAX_DEPTH,  # 20
            min_samples_split=self.config.MIN_SAMPLES_SPLIT,  # 100
            min_samples_leaf=self.config.MIN_SAMPLES_LEAF,  # 50
            max_features='sqrt',  # sqrt for regression
            random_state=self.config.RANDOM_STATE,
            verbose=2,
            n_jobs=self.config.N_JOBS,
            oob_score=True  # Free validation metric
        )
        self.model_reg.fit(self.X_reg_train, self.y_reg_train)
        logger.info("Regression model training completed")

        # Evaluate
        self._evaluate_regressor()

    def _evaluate_regressor(self):
        """Comprehensive regressor evaluation"""
        y_train_pred = self.model_reg.predict(self.X_reg_train)
        y_val_pred = self.model_reg.predict(self.X_reg_val)
        y_test_pred = self.model_reg.predict(self.X_reg_test)

        # MAE
        mae_train = mean_absolute_error(self.y_reg_train, y_train_pred)
        mae_val = mean_absolute_error(self.y_reg_val, y_val_pred)
        mae_test = mean_absolute_error(self.y_reg_test, y_test_pred)

        # RMSE
        rmse_train = np.sqrt(mean_squared_error(self.y_reg_train, y_train_pred))
        rmse_val = np.sqrt(mean_squared_error(self.y_reg_val, y_val_pred))
        rmse_test = np.sqrt(mean_squared_error(self.y_reg_test, y_test_pred))

        # R²
        r2_train = r2_score(self.y_reg_train, y_train_pred)
        r2_val = r2_score(self.y_reg_val, y_val_pred)
        r2_test = r2_score(self.y_reg_test, y_test_pred)

        logger.info(f"MAE - Train: {mae_train:.4f}, Val: {mae_val:.4f}, Test: {mae_test:.4f}")
        logger.info(f"RMSE - Train: {rmse_train:.4f}, Val: {rmse_val:.4f}, Test: {rmse_test:.4f}")
        logger.info(f"R² - Train: {r2_train:.4f}, Val: {r2_val:.4f}, Test: {r2_test:.4f}")

        # OOB Score
        if hasattr(self.model_reg, 'oob_score_'):
            logger.info(f"OOB Score: {self.model_reg.oob_score_:.4f}")

        # Feature importance
        self._log_feature_importance('regressor')

        # Check for overfitting
        if r2_train - r2_val > 0.10:
            logger.warning("Possible overfitting in regressor (train-val R² gap > 0.10)")

    def _log_feature_importance(self, model_type='classifier'):
        """Log top 20 most important features"""
        model = self.model_class if model_type == 'classifier' else self.model_reg

        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_names = model.feature_names_in_
            indices = np.argsort(importances)[::-1]

            logger.info(f"\nTop 20 Feature Importances ({model_type}):")
            for i in range(min(20, len(indices))):
                idx = indices[i]
                logger.info(f"  {i+1}. {feature_names[idx]}: {importances[idx]:.4f}")

    def save_models(self):
        """Save trained models to disk"""
        logger.info(f"Saving classifier to {self.config.CLASSIFIER_MODEL}")
        joblib.dump(self.model_class, self.config.CLASSIFIER_MODEL)

        logger.info(f"Saving regressor to {self.config.REGRESSOR_MODEL}")
        joblib.dump(self.model_reg, self.config.REGRESSOR_MODEL)

        logger.info("Models saved successfully")

    def train(self):
        """Complete training pipeline"""
        logger.info("Starting model training pipeline")

        self.load_and_prepare_data()
        self.train_classifier()
        self.train_regressor()
        self.save_models()

        logger.info("Training pipeline completed successfully!")
