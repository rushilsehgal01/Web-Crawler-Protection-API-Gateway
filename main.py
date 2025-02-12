"""
API Gateway - Main Entry Point

This module starts the FastAPI server using the modular gateway application.

The application is composed of independent modules following Single Responsibility:
- src/rate_limiting/ - Rate limiting logic
- src/metrics/ - Metrics collection
- src/backend/ - Backend service
- src/models/ - Data models
- src/gateway/ - API gateway orchestration
"""

import uvicorn
from src.gateway import create_app


if __name__ == "__main__":
    # Create the FastAPI application
    # Rate limiting: 100 requests per minute, tokens refill at ~0.167 per second (10 per minute)
    app = create_app(capacity=100, refill_rate=0.167)

    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
