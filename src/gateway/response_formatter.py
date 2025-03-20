"""
Response Formatter Module
Single responsibility: Format responses consistently.

This module ensures all API responses follow a consistent format.
"""

from typing import Dict, Any
from src.models import APIResponse


class ResponseFormatter:
    """Formats API responses."""

    @staticmethod
    def success(message: str, data: Dict[str, Any], client_ip: str = None) -> Dict[str, Any]:
        """Format a success response."""
        response_data = {
            "success": True,
            "message": message,
            "data": data
        }
        if client_ip:
            response_data["received_from_ip"] = client_ip
        return response_data

    @staticmethod
    def error(message: str, error: str) -> Dict[str, Any]:
        """Format an error response."""
        return APIResponse(
            success=False,
            message=message,
            error=error
        ).model_dump()

    @staticmethod
    def gateway_info() -> Dict[str, Any]:
        """Format gateway info response."""
        return {
            "service": "Rate-Limited API Gateway",
            "version": "1.0.0",
            "documentation": "/docs",
            "available_endpoints": {
                "POST /forward": "Forward request to backend service",
                "GET /metrics": "View gateway metrics",
                "GET /health": "Health check"
            }
        }
