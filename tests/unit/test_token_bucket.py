"""
Tests for TokenBucket Module
"""

import pytest
import time
from src.rate_limiting.token_bucket import TokenBucket


class TestTokenBucket:
    """Test token bucket rate limiting."""

    def test_initialization(self):
        """Bucket starts with full capacity."""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)
        assert bucket.tokens == 100
        assert bucket.capacity == 100

    def test_single_request_allowed(self):
        """First request consumes one token."""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)
        assert bucket.allow_request() is True
        assert bucket.tokens == 99

    def test_capacity_limit(self):
        """Can't use more tokens than capacity."""
        bucket = TokenBucket(capacity=5, refill_rate=10.0)
        for _ in range(5):
            assert bucket.allow_request() is True
        assert bucket.allow_request() is False

    def test_refill_rate(self):
        """Tokens refill at correct rate."""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)
        bucket.tokens = 0
        time.sleep(0.5)
        bucket._refill_tokens()
        # Should have ~5 tokens after 0.5 seconds
        assert 4 < bucket.tokens < 6

    def test_never_exceeds_capacity(self):
        """Tokens don't exceed capacity after refill."""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)
        bucket.tokens = 50
        time.sleep(0.2)
        bucket._refill_tokens()
        assert bucket.tokens <= 100
