"""
STONKS Dashboard Package

Professional-grade stock analysis dashboard built with Streamlit.

Main entry point: dashboard.main.run_dashboard()
Clean launcher: Use the root dashboard.py file

This package structure keeps everything organized and maintainable.
"""

from .main import run_dashboard

__version__ = "1.0.0"
__author__ = "STONKS Team"

__all__ = ['run_dashboard']