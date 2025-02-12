"""
Tests for Metrics Collector Module
"""

import pytest
from src.metrics.collector import MetricsCollector


class TestMetricsCollector:
    """Test metrics collection."""

    def test_initialization(self):
        """Collector starts at zero."""
        collector = MetricsCollector()
        assert collector.total_requests == 0
        assert collector.successful_requests == 0
        assert collector.blocked_requests == 0

    def test_record_successful(self):
        """Records successful requests."""
        collector = MetricsCollector()
        collector.record_request(was_blocked=False, response_time=0.05)

        assert collector.total_requests == 1
        assert collector.successful_requests == 1
        assert collector.blocked_requests == 0

    def test_record_blocked(self):
        """Records blocked requests."""
        collector = MetricsCollector()
        collector.record_request(was_blocked=True, response_time=0.01)

        assert collector.total_requests == 1
        assert collector.blocked_requests == 1
        assert collector.successful_requests == 0

    def test_response_times_only_for_successful(self):
        """Response times only recorded for successful requests."""
        collector = MetricsCollector()
        collector.record_request(was_blocked=False, response_time=0.1)
        collector.record_request(was_blocked=True, response_time=0.01)

        assert len(collector.response_times) == 1
        assert collector.response_times[0] == 0.1

    def test_reset(self):
        """Resets all metrics."""
        collector = MetricsCollector()
        collector.record_request(was_blocked=False, response_time=0.05)
        collector.reset()

        assert collector.total_requests == 0
        assert len(collector.response_times) == 0
