"""
Configuration management for Flight Delay Insurance
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Config:
    """Application configuration"""

    # Flask settings
    FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Model paths
    MODELS_DIR = Path(os.getenv('MODELS_DIR', BASE_DIR / 'models'))
    CLASSIFIER_MODEL = os.getenv('CLASSIFIER_MODEL', str(MODELS_DIR / 'flight_delay_classifier_v1.pkl'))
    REGRESSOR_MODEL = os.getenv('REGRESSOR_MODEL', str(MODELS_DIR / 'flight_delay_regressor_v1.pkl'))

    # Data paths
    DATA_DIR = Path(os.getenv('DATA_DIR', BASE_DIR / 'data'))
    FLIGHT_DATA_PATH = os.getenv('FLIGHT_DATA_PATH', str(DATA_DIR / 'flights_sample_3m.csv'))

    # Model settings
    DELAY_THRESHOLD = float(os.getenv('DELAY_THRESHOLD', '0.05'))
    RANDOM_STATE = int(os.getenv('RANDOM_STATE', '0'))

    # Prediction mode
    MODE = os.getenv('MODE', 'test')  # 'train' or 'test'

    # Insurance pricing
    POLICY_PRICES = {
        1: float(os.getenv('POLICY_PRICE_1', '72.24')),
        2: float(os.getenv('POLICY_PRICE_2', '84.98')),
        3: float(os.getenv('POLICY_PRICE_3', '95.50')),
        4: float(os.getenv('POLICY_PRICE_4', '105.00')),
    }
    DEFAULT_POLICY_PRICE = float(os.getenv('DEFAULT_POLICY_PRICE', '72.24'))

    # Pricing formula settings
    PRICE_INCREASE_PER_INTERVAL = float(os.getenv('PRICE_INCREASE_PER_INTERVAL', '0.1'))
    DELAY_INTERVAL_MINUTES = int(os.getenv('DELAY_INTERVAL_MINUTES', '10'))

    # Model training settings
    N_ESTIMATORS = int(os.getenv('N_ESTIMATORS', '200'))  # Increased from 40
    MAX_DEPTH = int(os.getenv('MAX_DEPTH', '20'))
    MIN_SAMPLES_SPLIT = int(os.getenv('MIN_SAMPLES_SPLIT', '100'))
    MIN_SAMPLES_LEAF = int(os.getenv('MIN_SAMPLES_LEAF', '50'))
    MAX_FEATURES = os.getenv('MAX_FEATURES', 'sqrt')
    TEST_SIZE = float(os.getenv('TEST_SIZE', '0.1'))
    N_JOBS = int(os.getenv('N_JOBS', '-1'))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', str(BASE_DIR / 'logs' / 'app.log'))

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        Path(cls.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
