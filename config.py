"""
Configuration settings for the Stonks Dashboard.
- Don't be a dumbass that gets your data stolen <3
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Data settings
DEFAULT_PERIOD = "2y"  # Default time period for stock data
CACHE_DURATION_HOURS = 1  # How long to cache data before refreshing

# Strategy settings
DEFAULT_SHORT_WINDOW = 50   # Short-term moving average
DEFAULT_LONG_WINDOW = 200   # Long-term moving average
INITIAL_CAPITAL = 10000     # Starting amount for backtesting

# Dashboard settings
PAGE_TITLE = "Stonks Dashboard 📈"
PAGE_ICON = "📊"

# API settings (add your keys to .env file)
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")
POLYGON_KEY = os.getenv("POLYGON_KEY")

# Benchmark symbol for comparison
BENCHMARK_SYMBOL = "SPY"  # S&P 500 ETF