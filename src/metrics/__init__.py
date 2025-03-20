"""
Metrics package - handles all metrics collection and reporting.

Modules:
- collector: Collects raw metrics data
- calculator: Calculates derived metrics
"""

from .metrics_manager import MetricsManager

__all__ = ["MetricsManager"]
