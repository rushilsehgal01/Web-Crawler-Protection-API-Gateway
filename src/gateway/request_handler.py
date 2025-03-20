"""
Request Handler Module
Single responsibility: Process incoming requests through the gateway.

This module:
- Checks rate limits
- Forwards to backend
- Handles errors
"""

import time
from typing import Tuple, Dict, Any
from src.rate_limiting import RateLimiter
from src.backend import BackendService
from src.models import APIResponse, RateLimitResponse


class GatewayRequestHandler:
    """Handles requests through the gateway pipeline."""

    def __init__(self, rate_limiter: RateLimiter, backend: BackendService):
        self.rate_limiter = rate_limiter
        self.backend = backend

    def handle(self, client_ip: str, endpoint: str, data: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """
        Process a gateway request.

        Args:
            client_ip: Client IP address
            endpoint: Backend endpoint
            data: Request data

        Returns:
            Tuple of (status_code, response_dict)
        """
        start_time = time.time()

        # Check rate limit
        if not self.rate_limiter.is_allowed(client_ip):
            return (429, RateLimitResponse().model_dump())

        # Forward to backend
        try:
            backend_response = self.backend.handle_request(endpoint, data)
            response_time = time.time() - start_time

            return (200, {
                "success": True,
                "message": f"Request received from {client_ip}",
                "data": backend_response,
                "received_from_ip": client_ip
            })

        except Exception as e:
            response_time = time.time() - start_time

            return (500, APIResponse(
                success=False,
                message="Error processing request",
                error=str(e)
            ).model_dump())
