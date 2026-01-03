#!/usr/bin/env python3
"""
Entry point for downloading dataset from Kaggle
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.data import download_dataset


def main():
    """Main download entry point"""
    success = download_dataset()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
