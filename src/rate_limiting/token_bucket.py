"""
Token Bucket Module
Single responsibility: Manage tokens for a single client.

This module implements the core token bucket algorithm:
- Tracks tokens available for a client
- Refills tokens based on elapsed time
- Determines if a request can be allowed
"""

import time


class TokenBucket:
    """
    A single client's token bucket for rate limiting.

    Args:
        capacity: Maximum tokens this bucket can hold
        refill_rate: Tokens added per second
    """

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity  # Start with full bucket
        self.last_refill_time = time.time()

    def allow_request(self) -> bool:
        """
        Check if a request should be allowed.

        Returns:
            True if token available, False otherwise
        """
        self._refill_tokens()

        if self.tokens >= 1:
            self.tokens -= 1
            return True

        return False

    def _refill_tokens(self) -> None:
        """Add tokens based on elapsed time since last refill."""
        now = time.time()
        time_elapsed = now - self.last_refill_time
        tokens_to_add = time_elapsed * self.refill_rate

        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill_time = now

    def get_remaining_tokens(self) -> int:
        """Get current token count (refills before returning)."""
        self._refill_tokens()
        return int(self.tokens)
