from flask import Flask, request, jsonify
import joblib
import pandas as pd

STANDARD_PRICE = 72.24  # Standard price for the insurance


class WebApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.model_class = joblib.load('flight_delay_classifier_v1.pkl')
        self.model_reg = joblib.load('flight_delay_regressor_v1.pkl')

    def calculate_insurance_price(self, is_delayed, delay_duration):
        if is_delayed:
            # Calculate the number of 10 minute intervals in the delay duration
            intervals = delay_duration // 10
            # Increase the insurance price by 10% for each 10 minute interval
            insurance_price = STANDARD_PRICE * (1 + 0.1 * intervals)
        else:
            insurance_price = STANDARD_PRICE
        return round(insurance_price, 2)

    def predict(self):
        @self.app.route('/predict', methods=['POST'])
        def predict():
            # Get the parameters from the request
            params = request.get_json(force=True)

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
            columns_without_delayed = [col for col in self.model_class.feature_names_in_]
            df_params = df_params.reindex(columns=columns_without_delayed, fill_value=0)

            # Predict if the flight will be delayed
            delay_proba = self.model_class.predict_proba(df_params)[:, 1][0]
            is_delayed = delay_proba > 0.05

            # If the flight is predicted to be delayed, predict the duration of the delay
            if is_delayed:
                delay_duration = self.model_reg.predict(df_params)[0]
            else:
                delay_duration = 0

            # Calculate the insurance price for the flight
            insurance_price = self.calculate_insurance_price(is_delayed, delay_duration)

            # Return the predictions and insurance price
            return jsonify({
                'insurance_price': insurance_price
            })

    def run(self):
        self.app.run(host='0.0.0.0', port=5000)


# Create an instance of the class and run the server
predictor = WebApp()
predictor.predict()
predictor.run()
