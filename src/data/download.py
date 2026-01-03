"""
Download flight delay dataset from Kaggle
Automatically places data in the correct location
"""

import os
import shutil
import logging
from pathlib import Path
import kagglehub
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def download_dataset():
    """Download the flight delay dataset from Kaggle"""

    try:
        logger.info("Starting dataset download from Kaggle...")
        logger.info("Dataset: patrickzel/flight-delay-and-cancellation-dataset-2019-2023")

        # Download latest version
        path = kagglehub.dataset_download("patrickzel/flight-delay-and-cancellation-dataset-2019-2023")

        logger.info(f"Dataset downloaded to: {path}")

        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)

        # Find CSV files in the downloaded path
        downloaded_path = Path(path)
        csv_files = list(downloaded_path.glob("*.csv"))

        if not csv_files:
            logger.error("No CSV files found in downloaded dataset")
            return False

        logger.info(f"Found {len(csv_files)} CSV file(s)")

        # Copy CSV files to data directory
        for csv_file in csv_files:
            dest_file = data_dir / csv_file.name
            logger.info(f"Copying {csv_file.name} to {dest_file}")
            shutil.copy2(csv_file, dest_file)

        # Update .env if it exists
        env_file = Path(".env")
        if env_file.exists():
            # Find the main CSV file (usually the largest or combined one)
            main_csv = max(csv_files, key=lambda x: x.stat().st_size)
            dest_csv = data_dir / main_csv.name

            logger.info(f"Setting FLIGHT_DATA_PATH to {dest_csv}")

            # Read existing .env
            with open(env_file, 'r') as f:
                env_content = f.read()

            # Update or add FLIGHT_DATA_PATH
            if 'FLIGHT_DATA_PATH=' in env_content:
                lines = env_content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('FLIGHT_DATA_PATH='):
                        lines[i] = f'FLIGHT_DATA_PATH={dest_csv}'
                env_content = '\n'.join(lines)
            else:
                env_content += f'\nFLIGHT_DATA_PATH={dest_csv}\n'

            # Write back
            with open(env_file, 'w') as f:
                f.write(env_content)

            logger.info("Updated .env with dataset path")

        logger.info("✓ Dataset download complete!")
        logger.info(f"✓ Data files available in: {data_dir.absolute()}")

        # Show file sizes
        logger.info("\nDownloaded files:")
        for csv_file in data_dir.glob("*.csv"):
            size_mb = csv_file.stat().st_size / (1024 * 1024)
            logger.info(f"  - {csv_file.name}: {size_mb:.2f} MB")

        return True

    except Exception as e:
        logger.error(f"Error downloading dataset: {e}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Ensure you have a Kaggle account")
        logger.error("2. Set up Kaggle API credentials:")
        logger.error("   - Go to https://www.kaggle.com/settings/account")
        logger.error("   - Create New API Token")
        logger.error("   - Place kaggle.json in ~/.kaggle/")
        logger.error("3. Accept dataset terms on Kaggle website")
        return False

if __name__ == "__main__":
    success = download_dataset()
    exit(0 if success else 1)
