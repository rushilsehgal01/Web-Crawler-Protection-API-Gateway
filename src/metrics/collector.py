"""
Metrics Collector Module
Single responsibility: Collect and store raw metrics data.

This module:
- Records individual requests
- Stores response times
- Tracks request counts
"""

from typing import List


class MetricsCollector:
    """Collects raw metrics data from requests."""

    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.blocked_requests = 0
        self.response_times: List[float] = []

    def record_request(self, was_blocked: bool, response_time: float) -> None:
        """
        Record a request.

        Args:
            was_blocked: True if rate limited
            response_time: Time in seconds to process
        """
        self.total_requests += 1

        if was_blocked:
            self.blocked_requests += 1
        else:
            self.successful_requests += 1
            self.response_times.append(response_time)

    def reset(self) -> None:
        """Clear all collected metrics."""
        self.total_requests = 0
        self.successful_requests = 0
        self.blocked_requests = 0
        self.response_times = []

    def get_raw_data(self) -> dict:
        """Get all raw collected data."""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "blocked_requests": self.blocked_requests,
            "response_times": self.response_times.copy()
        }
