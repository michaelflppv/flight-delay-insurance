"""
Flask API application for flight delay insurance predictions
"""

import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

from src.config import Config
from src.ml import FlightDelayPredictor

logger = logging.getLogger(__name__)


def create_app():
    """
    Create and configure the Flask application

    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    config = Config()

    # Enable CORS
    CORS(app)

    # Initialize predictor
    try:
        predictor = FlightDelayPredictor()
        models_loaded = predictor.models_loaded
    except Exception as e:
        logger.error(f"Failed to initialize predictor: {e}")
        predictor = None
        models_loaded = False

    # Error handlers
    @app.errorhandler(400)
    def bad_request(e):
        logger.warning(f"Bad request: {e}")
        return jsonify({'error': 'Bad request', 'message': str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        logger.warning(f"Not found: {e}")
        return jsonify({'error': 'Not found', 'message': str(e)}), 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    # Routes
    @app.route('/', methods=['GET'])
    def index():
        """Root endpoint with API information"""
        return jsonify({
            'name': 'Flight Delay Insurance API',
            'version': '0.1.0',
            'endpoints': {
                '/health': 'Health check endpoint',
                '/predict': 'Predict flight delay and calculate insurance price (POST)'
            }
        }), 200

    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        health_status = {
            'status': 'healthy' if models_loaded else 'degraded',
            'models_loaded': models_loaded,
            'classifier_path': str(config.CLASSIFIER_MODEL),
            'regressor_path': str(config.REGRESSOR_MODEL),
            'version': '0.1.0'
        }

        status_code = 200 if models_loaded else 503
        return jsonify(health_status), status_code

    @app.route('/predict', methods=['POST'])
    def predict():
        """Predict flight delay and calculate insurance price"""
        try:
            # Check if models are loaded
            if not models_loaded or predictor is None:
                logger.error("Prediction attempted but models not loaded")
                return jsonify({
                    'error': 'Models not available',
                    'message': 'ML models are not loaded. Please contact administrator.'
                }), 503

            # Validate request
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400

            params = request.get_json()
            logger.info(f"Received prediction request: {params}")

            # Validate required fields
            required_fields = [
                'AIRLINE_CODE', 'ORIGIN', 'DEST', 'DISTANCE',
                'CRS_DEP_TIME', 'FL_DATE'
            ]
            missing_fields = [f for f in required_fields if f not in params]
            if missing_fields:
                return jsonify({
                    'error': 'Validation error',
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400

            # Validate data types and ranges
            try:
                # CRS_DEP_TIME validation
                dep_time = int(params.get('CRS_DEP_TIME'))
                if not (0 <= dep_time <= 2359):
                    raise ValueError("CRS_DEP_TIME must be between 0 and 2359")

                # FL_DATE validation
                pd.to_datetime(params.get('FL_DATE'))

                # DISTANCE validation
                distance = float(params.get('DISTANCE'))
                if not (0 < distance < 10000):
                    raise ValueError("DISTANCE must be between 0 and 10000 miles")

                # Airport code validation (3-letter codes)
                origin = str(params.get('ORIGIN'))
                dest = str(params.get('DEST'))
                if len(origin) != 3:
                    raise ValueError("ORIGIN must be 3-letter airport code (e.g., 'DEN')")
                if len(dest) != 3:
                    raise ValueError("DEST must be 3-letter airport code (e.g., 'SFO')")

            except (TypeError, ValueError) as e:
                return jsonify({
                    'error': 'Validation error',
                    'message': str(e)
                }), 400

            # Extract policy ID and get base price
            policy_id = params.pop('POLICY_ID', None)
            base_price = config.POLICY_PRICES.get(policy_id, config.DEFAULT_POLICY_PRICE)
            logger.info(f"Using policy {policy_id} with base price ${base_price}")

            # Make prediction
            is_delayed, delay_probability, delay_duration = predictor.predict(params)

            # Calculate insurance price
            insurance_price = predictor.calculate_insurance_price(
                is_delayed, delay_duration, base_price
            )

            logger.info(f"Insurance price calculated: ${insurance_price}")

            # Return results
            return jsonify({
                'insurance_price': insurance_price,
                'delay_probability': round(delay_probability, 4),
                'is_delayed': bool(is_delayed),
                'predicted_delay_minutes': round(delay_duration, 2) if is_delayed else 0
            }), 200

        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return jsonify({'error': 'Validation error', 'message': str(e)}), 400
        except Exception as e:
            logger.error(f"Prediction error: {e}", exc_info=True)
            return jsonify({'error': 'Prediction failed', 'message': str(e)}), 500

    return app
