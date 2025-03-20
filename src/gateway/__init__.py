"""
Gateway package - core gateway logic and request handling.

Modules:
- request_handler: Processes incoming requests
- response_formatter: Formats outgoing responses
- routes: API endpoint definitions
- app: FastAPI application setup
"""

from .app import create_app

__all__ = ["create_app"]
