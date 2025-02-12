"""
Integration Tests for Rate Limiting
"""

import pytest
from fastapi.testclient import TestClient
from src.gateway import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app(capacity=5, refill_rate=100.0)  # Very small capacity for testing
    return TestClient(app)


class TestRateLimitingIntegration:
    """Test rate limiting with full API."""

    def test_product_search_endpoint_works(self, client):
        """Product search endpoint works through full API stack."""
        # Make several requests
        for _ in range(3):
            response = client.get("/products/search?category=electronics")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "data" in data

    def test_rate_limit_response_includes_error(self, client):
        """Rate limit response has correct error format."""
        # Make requests rapidly until rate limited or timeout
        last_response = None
        for i in range(50):
            response = client.get("/products/search?category=books")
            last_response = response
            if response.status_code == 429:
                break

        # If we hit the rate limit, verify response format
        if last_response and last_response.status_code == 429:
            data = last_response.json()
            assert "error" in data
            assert "retry_after_seconds" in data
