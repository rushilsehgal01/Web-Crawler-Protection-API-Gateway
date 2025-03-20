"""
Tests for Metrics Calculator Module
"""

import pytest
from src.metrics.calculator import MetricsCalculator


class TestMetricsCalculator:
    """Test metrics calculations."""

    def test_average_response_time(self):
        """Calculates average correctly."""
        calc = MetricsCalculator()
        times = [0.1, 0.2, 0.3]
        avg = calc.calculate_average_response_time(times)
        assert abs(avg - 0.2) < 0.01

    def test_average_empty_list(self):
        """Returns 0 for empty list."""
        calc = MetricsCalculator()
        avg = calc.calculate_average_response_time([])
        assert avg == 0.0

    def test_success_rate(self):
        """Calculates success rate correctly."""
        calc = MetricsCalculator()
        rate = calc.calculate_success_rate(total=100, successful=75)
        assert rate == 75.0

    def test_success_rate_zero_total(self):
        """Returns 0 when total is 0."""
        calc = MetricsCalculator()
        rate = calc.calculate_success_rate(total=0, successful=0)
        assert rate == 0.0

    def test_block_rate(self):
        """Calculates block rate correctly."""
        calc = MetricsCalculator()
        rate = calc.calculate_block_rate(total=100, blocked=25)
        assert rate == 25.0
