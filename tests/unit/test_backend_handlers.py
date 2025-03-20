"""
Tests for Backend Handlers Module
"""

import pytest
from src.backend.handlers import ProductSearchHandler, HealthHandler


class TestProductSearchHandler:
    """Test product search endpoint handler (crawler protection)."""

    def test_search_electronics(self):
        """Search electronics category."""
        handler = ProductSearchHandler()
        response = handler.handle({"category": "electronics", "page": 1, "limit": 10})

        assert response["status"] == "success"
        assert response["data"]["category"] == "electronics"
        assert len(response["data"]["results"]) <= 10
        assert response["data"]["total_results"] > 0

    def test_search_clothing(self):
        """Search clothing category."""
        handler = ProductSearchHandler()
        response = handler.handle({"category": "clothing"})

        assert response["status"] == "success"
        assert response["data"]["category"] == "clothing"
        assert len(response["data"]["results"]) > 0

    def test_search_invalid_category(self):
        """Search invalid category returns error."""
        handler = ProductSearchHandler()
        response = handler.handle({"category": "invalid"})

        assert response["status"] == "error"
        assert "not found" in response["message"].lower()

    def test_search_pagination(self):
        """Test pagination works correctly."""
        handler = ProductSearchHandler()

        # First page
        result1 = handler.handle({"category": "electronics", "page": 1, "limit": 2})
        assert len(result1["data"]["results"]) == 2

        # Second page
        result2 = handler.handle({"category": "electronics", "page": 2, "limit": 2})
        assert len(result2["data"]["results"]) <= 2

    def test_search_default_params(self):
        """Test default parameters."""
        handler = ProductSearchHandler()
        response = handler.handle({"category": "books"})

        assert response["data"]["page"] == 1
        assert response["data"]["limit"] == 20


class TestHealthHandler:
    """Test health endpoint handler."""

    def test_handle_health(self):
        """Returns health status."""
        handler = HealthHandler()
        response = handler.handle({})

        assert response["status"] == "healthy"
        assert "uptime_seconds" in response
        assert "version" in response
        assert response["service"] == "e-commerce-api-gateway"
        assert response["protected_by"] == "rate-limiter"
