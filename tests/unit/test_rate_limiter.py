"""
Tests for RateLimiter Module
"""

import pytest
from src.rate_limiting import RateLimiter


class TestRateLimiter:
    """Test rate limiter for multiple clients."""

    def test_initialization(self):
        """Rate limiter starts with no clients."""
        limiter = RateLimiter(capacity=100, refill_rate=10.0)
        assert len(limiter.clients) == 0

    def test_first_request_allowed(self):
        """First request from any client is allowed."""
        limiter = RateLimiter(capacity=100, refill_rate=10.0)
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client2") is True

    def test_independent_limits(self):
        """Each client has independent rate limits."""
        limiter = RateLimiter(capacity=5, refill_rate=10.0)

        # Client 1 uses all tokens
        for _ in range(5):
            assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is False

        # Client 2 still has tokens
        assert limiter.is_allowed("client2") is True

    def test_client_stats(self):
        """Returns accurate stats for clients."""
        limiter = RateLimiter(capacity=100, refill_rate=10.0)

        # Unknown client
        stats = limiter.get_client_stats("unknown")
        assert stats["capacity"] == 100
        assert stats["tokens_remaining"] == 100

        # Known client after using tokens
        limiter.is_allowed("client1")
        limiter.is_allowed("client1")
        stats = limiter.get_client_stats("client1")
        assert stats["tokens_remaining"] == 98
