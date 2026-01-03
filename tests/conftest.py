"""
Pytest configuration and fixtures
"""

import pytest
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_flight_data():
    """Sample flight data for testing"""
    return {
        'AIRLINE_CODE': 'NK',
        'ORIGIN_CITY': 'Denver, CO',
        'DEST_CITY': 'Houston, TX',
        'CRS_DEP_TIME': 1534,
        'FL_DATE': '2024-07-15'
    }


@pytest.fixture
def api_client():
    """Flask test client"""
    from src.api import create_app
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()
