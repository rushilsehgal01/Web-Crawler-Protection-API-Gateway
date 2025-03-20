"""
Backend package - handles all backend service logic.

Modules:
- base_handler: Base handler for backend requests
- users_handler: Handles /users endpoint
- data_handler: Handles /data endpoint
- health_handler: Handles /health endpoint
"""

from .service import BackendService

__all__ = ["BackendService"]
