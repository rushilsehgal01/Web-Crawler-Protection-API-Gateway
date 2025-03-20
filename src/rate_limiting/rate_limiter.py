"""
Rate Limiter Manager Module
Single responsibility: Manage rate limiting for multiple clients.

This module handles:
- Creating token buckets for new clients
- Checking rate limits per client
- Getting per-client statistics
"""

from typing import Dict
from .token_bucket import TokenBucket


class RateLimiter:
    """
    Manages rate limiting for multiple clients.
    Each client gets their own token bucket.

    Args:
        capacity: Max tokens per client
        refill_rate: Tokens per second per client
    """

    def __init__(self, capacity: int = 100, refill_rate: float = 10.0):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.clients: Dict[str, TokenBucket] = {}

    def is_allowed(self, client_id: str) -> bool:
        """
        Check if client can make a request.

        Args:
            client_id: Unique client identifier (e.g., IP address)

        Returns:
            True if allowed, False if rate limited
        """
        if client_id not in self.clients:
            self.clients[client_id] = TokenBucket(
                capacity=self.capacity,
                refill_rate=self.refill_rate
            )

        return self.clients[client_id].allow_request()

    def get_client_stats(self, client_id: str) -> Dict:
        """
        Get rate limit status for a client.

        Args:
            client_id: Unique client identifier

        Returns:
            Dict with tokens_remaining, capacity, refill_rate
        """
        if client_id not in self.clients:
            return {
                "tokens_remaining": self.capacity,
                "capacity": self.capacity,
                "refill_rate": self.refill_rate
            }

        bucket = self.clients[client_id]

        return {
            "tokens_remaining": bucket.get_remaining_tokens(),
            "capacity": bucket.capacity,
            "refill_rate": bucket.refill_rate
        }
