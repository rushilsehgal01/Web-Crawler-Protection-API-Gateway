"""
Backend Router Module
Single responsibility: Route requests to appropriate handlers.

This module manages handler registration and routing.
"""

from typing import Dict, Any
from .handlers import BaseHandler, ProductSearchHandler, HealthHandler


class BackendRouter:
    """Routes backend requests to appropriate handlers."""

    def __init__(self):
        self.handlers: Dict[str, BaseHandler] = {
            "/products/search": ProductSearchHandler(),
            "/health": HealthHandler(),
        }

    def handle_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route and handle a backend request.

        Args:
            endpoint: The endpoint path
            data: Request data

        Returns:
            Response from handler or error
        """
        handler = self.handlers.get(endpoint)

        if handler is None:
            return {"error": f"Endpoint {endpoint} not found"}

        return handler.handle(data)

    def register_handler(self, endpoint: str, handler: BaseHandler) -> None:
        """Register a custom handler for an endpoint."""
        self.handlers[endpoint] = handler
