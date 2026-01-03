#!/usr/bin/env python3
"""
Entry point for running the API server
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.utils import setup_logger
from src.config import Config
from src.api import create_app


def main():
    """Main server entry point"""
    config = Config()
    config.ensure_directories()

    # Set up logging
    logger = setup_logger('serve', config.LOG_FILE, config.LOG_LEVEL)
    logger.info(f"Starting Flask server on {config.FLASK_HOST}:{config.FLASK_PORT}")
    logger.info(f"Debug mode: {config.FLASK_DEBUG}")

    # Create and run app
    app = create_app()
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )


if __name__ == "__main__":
    main()
