#!/usr/bin/env python3
"""
Entry point for model training
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.utils import setup_logger
from src.config import Config
from src.ml import ModelTrainer


def main():
    """Main training entry point"""
    config = Config()
    config.ensure_directories()

    # Set up logging
    logger = setup_logger('train', config.LOG_FILE, config.LOG_LEVEL)
    logger.info("Starting model training")

    try:
        trainer = ModelTrainer()
        trainer.train()
        logger.info("Training completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
