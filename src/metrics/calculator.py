"""
Metrics Calculator Module
Single responsibility: Calculate derived metrics from raw data.

This module:
- Calculates averages
- Calculates percentages
- Derives insights from raw data
"""

from typing import List


class MetricsCalculator:
    """Calculates derived metrics from raw data."""

    @staticmethod
    def calculate_average_response_time(response_times: List[float]) -> float:
        """
        Calculate average response time.

        Args:
            response_times: List of response times

        Returns:
            Average in seconds, or 0 if empty
        """
        if not response_times:
            return 0.0
        return sum(response_times) / len(response_times)

    @staticmethod
    def calculate_success_rate(total: int, successful: int) -> float:
        """
        Calculate success rate as percentage.

        Args:
            total: Total requests
            successful: Successful requests

        Returns:
            Percentage (0-100)
        """
        if total == 0:
            return 0.0
        return (successful / total) * 100

    @staticmethod
    def calculate_block_rate(total: int, blocked: int) -> float:
        """
        Calculate block rate as percentage.

        Args:
            total: Total requests
            blocked: Blocked requests

        Returns:
            Percentage (0-100)
        """
        if total == 0:
            return 0.0
        return (blocked / total) * 100
