"""
FastAPI Application Module
Single responsibility: Create and configure FastAPI application.

This module sets up the app, middleware, and routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.rate_limiting import RateLimiter
from src.metrics import MetricsManager
from src.backend import BackendService
from .routes import create_routes


def create_app(
    capacity: int = 100,
    refill_rate: float = 10.0
) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        capacity: Rate limit capacity per client
        refill_rate: Token refill rate per second

    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title="Rate-Limited API Gateway",
        description="A backend service demonstrating rate limiting and metrics",
        version="1.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize components
    rate_limiter = RateLimiter(capacity=capacity, refill_rate=refill_rate)
    metrics_manager = MetricsManager()
    backend_service = BackendService()

    # Include routes
    routes = create_routes(rate_limiter, metrics_manager, backend_service)
    app.include_router(routes)

    # Store in app state for access if needed
    app.state.rate_limiter = rate_limiter
    app.state.metrics_manager = metrics_manager
    app.state.backend_service = backend_service

    return app
