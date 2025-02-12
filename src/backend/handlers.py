"""
Backend Handlers Module
Single responsibility: Each handler manages a single endpoint.

Handlers:
- ProductSearchHandler: Searches products by category (web crawler protection)
- HealthHandler: Returns service health status
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import time


class BaseHandler(ABC):
    """Base class for all backend handlers."""

    def simulate_delay(self) -> None:
        """Simulate network latency (10-100ms)."""
        import random
        delay = random.uniform(0.01, 0.1)
        time.sleep(delay)

    @abstractmethod
    def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a request. Must be implemented by subclass."""
        pass


class ProductSearchHandler(BaseHandler):
    """Handles /products/search endpoint (anti-crawler protection)."""

    PRODUCTS_DB = {
        "electronics": [
            {"id": 1, "name": "Laptop", "price": 999.99, "in_stock": True},
            {"id": 2, "name": "USB Cable", "price": 9.99, "in_stock": True},
            {"id": 3, "name": "Monitor", "price": 299.99, "in_stock": False},
            {"id": 4, "name": "Keyboard", "price": 79.99, "in_stock": True},
            {"id": 5, "name": "Mouse", "price": 29.99, "in_stock": True},
        ],
        "clothing": [
            {"id": 101, "name": "T-Shirt", "price": 19.99, "in_stock": True},
            {"id": 102, "name": "Jeans", "price": 49.99, "in_stock": True},
            {"id": 103, "name": "Jacket", "price": 99.99, "in_stock": False},
            {"id": 104, "name": "Sneakers", "price": 89.99, "in_stock": True},
        ],
        "books": [
            {"id": 201, "name": "Python Guide", "price": 39.99, "in_stock": True},
            {"id": 202, "name": "System Design", "price": 49.99, "in_stock": True},
            {"id": 203, "name": "Web Dev 101", "price": 29.99, "in_stock": False},
        ],
        "home": [
            {"id": 301, "name": "Pillow", "price": 24.99, "in_stock": True},
            {"id": 302, "name": "Blanket", "price": 59.99, "in_stock": True},
            {"id": 303, "name": "Desk Lamp", "price": 44.99, "in_stock": True},
        ],
    }

    def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Search for products by category (crawler protected)."""
        self.simulate_delay()

        category = data.get("category", "electronics").lower()
        page = data.get("page", 1)
        limit = data.get("limit", 20)

        # Validate category
        if category not in self.PRODUCTS_DB:
            return {
                "status": "error",
                "message": f"Category '{category}' not found. Available: {list(self.PRODUCTS_DB.keys())}"
            }

        # Get products for category
        products = self.PRODUCTS_DB[category]
        total_results = len(products)

        # Handle pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_results = products[start:end]

        return {
            "status": "success",
            "data": {
                "category": category,
                "page": page,
                "limit": limit,
                "total_results": total_results,
                "total_pages": (total_results + limit - 1) // limit,
                "results": paginated_results
            }
        }


class HealthHandler(BaseHandler):
    """Handles /health endpoint."""

    def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Return service health status."""
        self.simulate_delay()
        return {
            "status": "healthy",
            "service": "e-commerce-api-gateway",
            "uptime_seconds": 3600,
            "version": "1.0.0",
            "protected_by": "rate-limiter"
        }
