"""
Integration Tests for API Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.gateway import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


class TestAPIEndpoints:
    """Test API endpoints."""

    def test_root_endpoint(self, client):
        """Root endpoint returns gateway info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Rate-Limited API Gateway"

    def test_health_endpoint(self, client):
        """Health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_products_search_valid_request(self, client):
        """Product search endpoint accepts valid requests."""
        response = client.get("/products/search?category=electronics")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["status"] == "success"

    def test_products_search_with_pagination(self, client):
        """Product search endpoint supports pagination."""
        response = client.get("/products/search?category=clothing&page=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["data"]["results"]) <= 2

    def test_metrics_endpoint(self, client):
        """Metrics endpoint returns metrics."""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "success_rate_percent" in data

    def test_reset_metrics_endpoint(self, client):
        """Reset metrics endpoint works."""
        response = client.post("/reset-metrics")
        assert response.status_code == 200

    def test_client_status_endpoint(self, client):
        """Client status endpoint returns rate limit info."""
        response = client.get("/client-status/127.0.0.1")
        assert response.status_code == 200
        data = response.json()
        assert "rate_limit_status" in data
