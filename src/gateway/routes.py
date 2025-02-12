"""
Routes Module
Single responsibility: Define API routes/endpoints.

This module registers all endpoints without containing business logic.
"""

from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse

from src.rate_limiting import RateLimiter
from src.metrics import MetricsManager
from src.backend import BackendService
from src.models import ProductSearchRequest, RateLimitResponse
from .request_handler import GatewayRequestHandler
from .response_formatter import ResponseFormatter


def create_routes(
    rate_limiter: RateLimiter,
    metrics_manager: MetricsManager,
    backend_service: BackendService
) -> APIRouter:
    """
    Create and configure API routes.

    Args:
        rate_limiter: Rate limiter instance
        metrics_manager: Metrics manager instance
        backend_service: Backend service instance

    Returns:
        Configured APIRouter
    """
    router = APIRouter()
    request_handler = GatewayRequestHandler(rate_limiter, backend_service)
    formatter = ResponseFormatter()

    @router.get("/")
    async def root():
        """Gateway info endpoint."""
        return formatter.gateway_info()

    @router.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "api-gateway"}

    @router.get("/products/search")
    async def search_products(
        request: Request,
        category: str = Query(..., description="Product category"),
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(20, ge=1, le=50, description="Results per page")
    ):
        """
        Search for products by category.

        This endpoint demonstrates rate limiting to protect against web crawlers.
        Crawlers trying to scrape all products get rate limited after ~100 requests.

        Args:
            category: Product category (electronics, clothing, books, home)
            page: Page number for pagination (default: 1)
            limit: Results per page (default: 20, max: 50)
        """
        client_ip = request.client.host

        status_code, response_data = request_handler.handle(
            client_ip=client_ip,
            endpoint="/products/search",
            data={"category": category, "page": page, "limit": limit}
        )

        # Record metrics
        was_blocked = status_code == 429
        metrics_manager.record_request(was_blocked, 0.0)  # Time recorded in handler

        return JSONResponse(status_code=status_code, content=response_data)

    @router.get("/metrics")
    async def get_metrics():
        """Get gateway metrics."""
        return metrics_manager.get_metrics()

    @router.post("/reset-metrics")
    async def reset_metrics():
        """Reset metrics to zero."""
        metrics_manager.reset()
        return {"message": "Metrics have been reset"}

    @router.get("/client-status/{client_ip}")
    async def get_client_status(client_ip: str):
        """Get rate limit status for a client."""
        stats = rate_limiter.get_client_stats(client_ip)
        return {
            "client_ip": client_ip,
            "rate_limit_status": stats
        }

    return router
