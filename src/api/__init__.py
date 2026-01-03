"""API server for flight delay predictions"""

from .app import create_app

__all__ = ["create_app"]
