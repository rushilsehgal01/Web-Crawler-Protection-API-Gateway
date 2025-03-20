"""
Backend Service Module
Single responsibility: Provide unified interface to backend operations.

This module uses router to handle requests.
"""

from typing import Dict, Any
from .router import BackendRouter


class BackendService:
    """
    Unified interface to backend service.

    Delegates to BackendRouter for request handling.
    """

    def __init__(self):
        self.router = BackendRouter()

    def handle_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a backend request.

        Args:
            endpoint: The endpoint path
            data: Request data

        Returns:
            Response from backend
        """
        return self.router.handle_request(endpoint, data)

    def register_handler(self, endpoint: str, handler) -> None:
        """Register a custom handler."""
        self.router.register_handler(endpoint, handler)
