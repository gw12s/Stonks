"""
Dashboard Components Package

All the modular pieces that make the dashboard work beautifully.
Import what you need, when you need it.

Because monolithic code is so 2010.
"""

from .sidebar import render_sidebar
from .data_loader import load_and_cache_data, load_sample_chart, validate_data
from .charts import create_strategy_charts, create_price_and_signals_chart
from .metrics import display_strategy_metrics, display_performance_summary

# Make commonly used functions easily accessible
__all__ = [
    'render_sidebar',
    'load_and_cache_data', 
    'load_sample_chart',
    'validate_data',
    'create_strategy_charts',
    'create_price_and_signals_chart', 
    'display_strategy_metrics',
    'display_performance_summary'
]