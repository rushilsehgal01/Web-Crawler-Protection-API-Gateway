"""
Metrics Manager Module
Single responsibility: Orchestrate metrics collection and calculation.

This module brings together collector and calculator to provide
the main metrics interface.
"""

from typing import Dict
from .collector import MetricsCollector
from .calculator import MetricsCalculator


class MetricsManager:
    """
    Orchestrates metrics collection and calculation.

    Uses:
    - MetricsCollector for raw data
    - MetricsCalculator for derived metrics
    """

    def __init__(self):
        self.collector = MetricsCollector()
        self.calculator = MetricsCalculator()

    def record_request(self, was_blocked: bool, response_time: float) -> None:
        """Record a request."""
        self.collector.record_request(was_blocked, response_time)

    def get_metrics(self) -> Dict:
        """
        Get all calculated metrics.

        Returns:
            Dictionary with all metrics
        """
        raw_data = self.collector.get_raw_data()

        avg_response_time = self.calculator.calculate_average_response_time(
            raw_data["response_times"]
        )
        success_rate = self.calculator.calculate_success_rate(
            raw_data["total_requests"],
            raw_data["successful_requests"]
        )
        block_rate = self.calculator.calculate_block_rate(
            raw_data["total_requests"],
            raw_data["blocked_requests"]
        )

        return {
            "total_requests": raw_data["total_requests"],
            "successful_requests": raw_data["successful_requests"],
            "blocked_requests": raw_data["blocked_requests"],
            "average_response_time_seconds": round(avg_response_time, 4),
            "success_rate_percent": round(success_rate, 2),
            "block_rate_percent": round(block_rate, 2)
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.collector.reset()
