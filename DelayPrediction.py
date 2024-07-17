"""
Author: Mikhail Filippov (University of Mannheim)
Version: 15.07.2024
"""

import numpy as np  # Import NumPy for numerical operations
import pandas as pd  # Import Pandas for data manipulation and analysis
# Import RandomForestClassifier and RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
# Import metrics for model evaluation
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score, mean_absolute_error
# Import train_test_split for data splitting
from sklearn.model_selection import train_test_split
# Import compute_class_weight to compute class weights
from sklearn.utils.class_weight import compute_class_weight
import gc  # Import gc for garbage collection
import joblib  # Import joblib for saving and loading models
import warnings  # Import the warnings module to handle warnings

warnings.filterwarnings("ignore")  # Filter and suppress warnings

# Set Pandas options to display a maximum of 1000 rows
pd.set_option('display.max_rows', 1000)

# Set the mode to 'train' to train the models, 'test' to make predictions
mode = "test"

# Importing necessary libraries and reading CSV files into pandas DataFrames
selected_columns = ['ARR_DELAY', 'AIRLINE_CODE', 'ORIGIN_CITY', 'DEST_CITY', 'CRS_DEP_TIME', 'FL_DATE']
df = pd.read_csv(r"C:\Users\mikef\Desktop\flights_sample_3m.csv\flights_sample_3m.csv",
                 usecols=selected_columns)
item0 = df.shape[0]
df = df.drop_duplicates()
item1 = df.shape[0]
print(f"Number of duplicates: {item0 - item1}")
gc.collect()

# Extract month, weekday, year, and planned departure hour from the 'FL_DATE' and 'CRS_DEP_TIME' columns
df['FL_DATE'] = pd.to_datetime(df['FL_DATE'])
df['Month'] = df['FL_DATE'].dt.month_name()
df['Weekday'] = df['FL_DATE'].dt.day_name()
df['Year'] = df['FL_DATE'].dt.year
df['Planned_departure_hour'] = df['CRS_DEP_TIME'] // 100

# Drop unused columns
selected_cols = ['ARR_DELAY', 'AIRLINE_CODE', 'ORIGIN_CITY', 'DEST_CITY', 'Planned_departure_hour', 'Month', 'Weekday',
                 'Year']
df = df[selected_cols]

# Display the shape of the resulting DataFrame 'df'
print(df.shape)

# Handle missing values for ARR_DELAY
df['ARR_DELAY'] = df['ARR_DELAY'].fillna(0)

# Create classification and regression datasets
classification_label = 'ARR_DELAY'

# Classification dataset
df['DELAYED'] = df['ARR_DELAY'] > 0
X_class = df.drop(['DELAYED', 'ARR_DELAY'], axis=1)
y_class = df['DELAYED'].values.reshape(-1, )

# Regression dataset
X_reg = df[df['ARR_DELAY'] > 0].drop(['DELAYED', 'ARR_DELAY'], axis=1)
y_reg = df[df['ARR_DELAY'] > 0]['ARR_DELAY'].values.reshape(-1, )

# Split the data into training and testing sets
cat_cols = df.select_dtypes(include=['object']).columns
cat_cols_idx = [list(X_class.columns).index(c) for c in cat_cols]

# Convert categorical variables to dummy variables
X_class = pd.get_dummies(X_class, columns=cat_cols)
X_reg = pd.get_dummies(X_reg, columns=cat_cols)

# Split the data into training and testing sets
X_class_train, X_class_test, y_class_train, y_class_test = train_test_split(X_class, y_class, test_size=0.1,
                                                                            random_state=0, stratify=y_class)
X_reg_train, X_reg_test, y_reg_train, y_reg_test = train_test_split(X_reg, y_reg, test_size=0.1, random_state=0)

# Display the shapes of the resulting datasets
print(X_class_train.shape, X_class_test.shape, y_class_train.shape, y_class_test.shape)
print(X_reg_train.shape, X_reg_test.shape, y_reg_train.shape, y_reg_test.shape)

# Clear memory by deleting the variables that are no longer needed and running garbage collection
del df
gc.collect()

if mode == "train":
    # Add class weights to handle class imbalance
    classes = np.unique(y_class_train)
    weights = compute_class_weight(class_weight='balanced', classes=classes, y=y_class_train)
    class_weights = dict(zip(classes, weights))
    print(class_weights)

    # Initialize and train the classification model
    model_class = RandomForestClassifier(n_estimators=40, class_weight=class_weights, random_state=0, verbose=2,
                                         n_jobs=-1)
    model_class.fit(X_class_train, y_class_train)

    # Make the prediction using the resulting model
    y_class_train_pred_proba = model_class.predict_proba(X_class_train)[:, 1]
    y_class_test_pred_proba = model_class.predict_proba(X_class_test)[:, 1]

    # Evaluate the classification model
    roc_auc_train = roc_auc_score(y_class_train, y_class_train_pred_proba,
                                  sample_weight=[class_weights[label] for label in y_class_train])
    roc_auc_test = roc_auc_score(y_class_test, y_class_test_pred_proba,
                                 sample_weight=[class_weights[label] for label in y_class_test])
    print(f"ROC AUC score for train {round(roc_auc_train, 4)}, and for test {round(roc_auc_test, 4)}")

    # Train accuracy
    y_class_train_pred = model_class.predict(X_class_train)
    train_accuracy = accuracy_score(y_class_train, y_class_train_pred)
    print(f"Training Accuracy: {train_accuracy}")

    # Test accuracy
    y_class_test_pred = model_class.predict(X_class_test)
    test_accuracy = accuracy_score(y_class_test, y_class_test_pred)
    print(f"Testing Accuracy: {test_accuracy}")

    # Classification report and confusion matrix for test data
    print("Classification Report for Test Data:")
    print(classification_report(y_class_test, y_class_test_pred))

    print("Confusion Matrix for Test Data:")
    print(confusion_matrix(y_class_test, y_class_test_pred))

    # Save the classification model
    joblib.dump(model_class, 'flight_delay_classifier_v1.pkl')

    # Initialize and train the regression model
    model_reg = RandomForestRegressor(n_estimators=40, random_state=0, verbose=2, n_jobs=-1)
    model_reg.fit(X_reg_train, y_reg_train)

    # Evaluate the regression model
    y_reg_train_pred = model_reg.predict(X_reg_train)
    y_reg_test_pred = model_reg.predict(X_reg_test)
    mae_train = mean_absolute_error(y_reg_train, y_reg_train_pred)
    mae_test = mean_absolute_error(y_reg_test, y_reg_test_pred)
    print(f"Mean Absolute Error for train {round(mae_train, 4)}, and for test {round(mae_test, 4)}")

    # Save the regression model
    joblib.dump(model_reg, 'flight_delay_regressor_v1.pkl')

elif mode == "test":
    # Load the classification model
    model_class = joblib.load('flight_delay_classifier_v1.pkl')

    # Load the regression model
    model_reg = joblib.load('flight_delay_regressor_v1.pkl')

    # Example usage
    params = {
        'AIRLINE_CODE': 'NK',
        'ORIGIN_CITY': 'Denver, CO',
        'DEST_CITY': 'Houston, TX',
        'CRS_DEP_TIME': 1534,
        'FL_DATE': '2024-07-15'
    }

    # Convert the parameters to a DataFrame
    df_params = pd.DataFrame([params])

    df_params['FL_DATE'] = pd.to_datetime(df_params['FL_DATE'])
    df_params['Month'] = df_params['FL_DATE'].dt.month_name()
    df_params['Weekday'] = df_params['FL_DATE'].dt.day_name()
    df_params['Year'] = df_params['FL_DATE'].dt.year
    df_params['Planned_departure_hour'] = df_params['CRS_DEP_TIME'] // 100

    # Drop unused columns
    selected_cols = ['AIRLINE_CODE', 'ORIGIN_CITY', 'DEST_CITY', 'Planned_departure_hour', 'Month',
                     'Weekday', 'Year']
    df_params = df_params[selected_cols]

    # Convert categorical variables to dummy variables
    df_params = pd.get_dummies(df_params)

    # Ensure the DataFrame has the same columns as the training data
    columns_without_delayed = [col for col in X_class_train.columns if col != 'DELAYED']
    df_params = df_params.reindex(columns=columns_without_delayed, fill_value=0)

    # Predict if the flight will be delayed
    delay_proba = model_class.predict_proba(df_params)[:, 1][0]
    is_delayed = delay_proba > 0.05

    # If the flight is predicted to be delayed, predict the duration of the delay
    if is_delayed:
        delay_duration = model_reg.predict(df_params)[0]
    else:
        delay_duration = 0

    # Print the predictions
    print(f"Is delayed: {is_delayed}, Delay duration: {delay_duration} minutes")

    # Define a standard price for the insurance
    STANDARD_PRICE = 50  # This can be adjusted as per your requirements

    # Define a function to calculate the insurance price based on the delay duration
    def calculate_insurance_price(is_delayed, delay_duration):
        if is_delayed:
            # If the flight is predicted to be delayed, increase the insurance price relative to the delay duration
            # Here, we're assuming that the insurance price increases by 1% for each minute of delay
            insurance_price = STANDARD_PRICE * (1 + delay_duration / 6000)
        else:
            # If the flight is not predicted to be delayed, the insurance price is the standard price
            insurance_price = STANDARD_PRICE

        return round(insurance_price, 2)


    # Calculate the insurance price for the flight
    insurance_price = calculate_insurance_price(is_delayed, delay_duration)

    # Print the insurance price
    print(f"Insurance price: {insurance_price} dollars")
