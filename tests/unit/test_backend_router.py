"""
Tests for Backend Router Module
"""

import pytest
from src.backend.router import BackendRouter


class TestBackendRouter:
    """Test backend request routing."""

    def test_route_product_search(self):
        """Routes to product search handler."""
        router = BackendRouter()
        response = router.handle_request("/products/search", {"category": "electronics"})

        assert response["status"] == "success"
        assert response["data"]["category"] == "electronics"
        assert len(response["data"]["results"]) > 0

    def test_route_product_search_clothing(self):
        """Routes to product search handler for clothing."""
        router = BackendRouter()
        response = router.handle_request("/products/search", {"category": "clothing"})

        assert response["status"] == "success"
        assert response["data"]["category"] == "clothing"

    def test_route_health(self):
        """Routes to health handler."""
        router = BackendRouter()
        response = router.handle_request("/health", {})

        assert response["status"] == "healthy"
        assert response["service"] == "e-commerce-api-gateway"

    def test_unknown_endpoint(self):
        """Returns error for unknown endpoint."""
        router = BackendRouter()
        response = router.handle_request("/unknown", {})

        assert "error" in response
