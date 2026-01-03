"""
Flight delay prediction using trained ML models
"""

import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any

from src.config import Config

logger = logging.getLogger(__name__)


class FlightDelayPredictor:
    """Predict flight delays using trained RandomForest models"""

    def __init__(self):
        """Initialize predictor and load models"""
        self.config = Config()
        self.model_class = None
        self.model_reg = None
        self.models_loaded = False

        self._load_models()

    def _load_models(self):
        """Load trained models from disk"""
        try:
            logger.info(f"Loading classification model from {self.config.CLASSIFIER_MODEL}")
            self.model_class = joblib.load(self.config.CLASSIFIER_MODEL)

            logger.info(f"Loading regression model from {self.config.REGRESSOR_MODEL}")
            self.model_reg = joblib.load(self.config.REGRESSOR_MODEL)

            self.models_loaded = True
            logger.info("Models loaded successfully")

        except FileNotFoundError as e:
            logger.error(f"Model file not found: {e}")
            logger.error("Please train models first using: make train")
            self.models_loaded = False

        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.models_loaded = False

    def _prepare_features(self, params: Dict[str, Any]) -> pd.DataFrame:
        """
        CRITICAL: Must match trainer.py feature engineering exactly!

        Args:
            params: Dictionary of flight parameters

        Returns:
            DataFrame with engineered features
        """
        # Convert to DataFrame
        df = pd.DataFrame([params])

        # Feature engineering (IDENTICAL to trainer.py)
        df['FL_DATE'] = pd.to_datetime(df['FL_DATE'])
        df['Month'] = df['FL_DATE'].dt.month  # Numeric
        df['Weekday'] = df['FL_DATE'].dt.dayofweek  # 0-6
        df['Quarter'] = df['FL_DATE'].dt.quarter
        df['Planned_departure_hour'] = df['CRS_DEP_TIME'] // 100

        # Cyclical encoding (must match trainer.py)
        df['Month_sin'] = np.sin(2 * np.pi * df['Month'] / 12)
        df['Month_cos'] = np.cos(2 * np.pi * df['Month'] / 12)
        df['Hour_sin'] = np.sin(2 * np.pi * df['Planned_departure_hour'] / 24)
        df['Hour_cos'] = np.cos(2 * np.pi * df['Planned_departure_hour'] / 24)
        df['Weekday_sin'] = np.sin(2 * np.pi * df['Weekday'] / 7)
        df['Weekday_cos'] = np.cos(2 * np.pi * df['Weekday'] / 7)

        # Select features (must match trainer.py selected_cols)
        selected_cols = [
            'AIRLINE_CODE', 'ORIGIN', 'DEST', 'DISTANCE',
            'Planned_departure_hour', 'Quarter',
            'Month_sin', 'Month_cos', 'Hour_sin', 'Hour_cos',
            'Weekday_sin', 'Weekday_cos'
        ]
        df = df[selected_cols]

        # One-hot encoding for categorical
        cat_cols = ['AIRLINE_CODE', 'ORIGIN', 'DEST']
        df = pd.get_dummies(df, columns=cat_cols)

        # Align with training features
        df = df.reindex(columns=self.model_class.feature_names_in_, fill_value=0)

        return df

    def predict(self, params: Dict[str, Any]) -> Tuple[bool, float, float]:
        """
        Predict flight delay

        Args:
            params: Flight parameters dict with keys:
                   - AIRLINE_CODE
                   - ORIGIN_CITY
                   - DEST_CITY
                   - CRS_DEP_TIME
                   - FL_DATE

        Returns:
            Tuple of (is_delayed, delay_probability, delay_duration_minutes)
        """
        if not self.models_loaded:
            raise RuntimeError("Models not loaded. Cannot make predictions.")

        # Prepare features
        df_features = self._prepare_features(params)

        # Predict delay probability
        delay_proba = self.model_class.predict_proba(df_features)[:, 1][0]
        is_delayed = delay_proba > self.config.DELAY_THRESHOLD

        logger.info(f"Delay probability: {delay_proba:.4f}, Is delayed: {is_delayed}")

        # Predict delay duration if delayed
        if is_delayed:
            delay_duration = self.model_reg.predict(df_features)[0]
            logger.info(f"Predicted delay duration: {delay_duration:.2f} minutes")
        else:
            delay_duration = 0.0

        return is_delayed, float(delay_proba), float(delay_duration)

    def calculate_insurance_price(
        self,
        is_delayed: bool,
        delay_duration: float,
        base_price: float
    ) -> float:
        """
        Calculate insurance price based on delay prediction

        Args:
            is_delayed: Whether flight is predicted to be delayed
            delay_duration: Predicted delay duration in minutes
            base_price: Base insurance price

        Returns:
            Calculated insurance price
        """
        if is_delayed:
            intervals = delay_duration // self.config.DELAY_INTERVAL_MINUTES
            price = base_price * (
                1 + self.config.PRICE_INCREASE_PER_INTERVAL * intervals
            )
        else:
            price = base_price

        return round(price, 2)
