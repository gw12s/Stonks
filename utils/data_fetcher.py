"""
   _____ _______ ____  _   _ _  __ _____ 
  / ____|__   __/ __ \| \ | | |/ // ____|
 | (___    | | | |  | |  \| | ' /| (___  
  \___ \   | | | |  | | . ` |  <  \___ \ 
  ____) |  | | | |__| | |\  | . \ ____) |
 |_____/   |_|  \____/|_| \_|_|\_\_____/ 
                                         
Data Fetcher - Get that market data! 📈

This module handles all stock data fetching with:
- Caching to avoid unnecessary API calls
- Error handling for when APIs are down
- Multiple data sources (Yahoo Finance primary)
- Proper data validation
"""

import yfinance as yf
import pandas as pd
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from utils.logger import setup_logger
from config import DATA_DIR, CACHE_DURATION_HOURS, DEFAULT_PERIOD

# Set up logging
logger = setup_logger(__name__)


class DataFetcher:
    """
    Handles stock data fetching with intelligent caching.
    """
    
    def __init__(self, cache_hours: int = CACHE_DURATION_HOURS):
        """
        Initialize the data fetcher.
        
        Args:
            cache_hours: How long to cache data before refreshing
        """
        self.cache_hours = cache_hours
        self.cache_dir = DATA_DIR / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        logger.info(f"DataFetcher initialized with {cache_hours}h cache")
    
    def get_stock_data(
        self, 
        symbol: str, 
        period: str = DEFAULT_PERIOD,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Get stock data with caching.
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL', 'TSLA')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            force_refresh: Skip cache and fetch fresh data
        
        Returns:
            DataFrame with OHLCV data and Date index
        
        Raises:
            ValueError: If symbol is invalid or data can't be fetched
        """
        symbol = symbol.upper().strip()
        cache_file = self.cache_dir / f"{symbol}_{period}.pkl"
        
        # Check if we have valid cached data
        if not force_refresh and self._is_cache_valid(cache_file):
            logger.info(f"Loading cached data for {symbol}")
            return self._load_cache(cache_file)
        
        # Fetch fresh data
        logger.info(f"Fetching fresh data for {symbol} ({period})")
        try:
            data = self._fetch_from_yahoo(symbol, period)
            self._save_cache(data, cache_file)
            return data
        
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
            # Try to return stale cache if available
            if cache_file.exists():
                logger.warning(f"Returning stale cache for {symbol}")
                return self._load_cache(cache_file)
            raise ValueError(f"Could not fetch data for {symbol}: {e}")
    
    def _fetch_from_yahoo(self, symbol: str, period: str) -> pd.DataFrame:
        """
        Fetch data from Yahoo Finance.

        Why Yahoo? It's for OLD PEOPLE?!
        - Free, no API key required
        - Reliable for most stocks
        - Good historical data coverage.. old is sometimes better 
        """
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if data.empty:
            raise ValueError(f"No data found for symbol {symbol}")
        
        # Clean up the data
        data = data.round(2)  # Round to 2 decimal places
        data.index.name = 'Date'
        
        # Add some basic technical indicators because it would be weird if we didn't
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['SMA_200'] = data['Close'].rolling(window=200).mean()
        
        logger.info(f"Fetched {len(data)} rows for {symbol}")
        return data
    
    def _is_cache_valid(self, cache_file: Path) -> bool:
        """Check if cached file exists and is within cache duration."""
        if not cache_file.exists():
            return False
        
        file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        expiry_time = datetime.now() - timedelta(hours=self.cache_hours)
        
        return file_time > expiry_time
    
    def _save_cache(self, data: pd.DataFrame, cache_file: Path) -> None:
        """Save data to cache file."""
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            logger.debug(f"Cached data to {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to cache data: {e}")
    
    def _load_cache(self, cache_file: Path) -> pd.DataFrame:
        """Load data from cache file."""
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    def get_multiple_stocks(self, symbols: list, period: str = DEFAULT_PERIOD) -> Dict[str, pd.DataFrame]:
        """
        Get data for multiple stocks.
        
        Args:
            symbols: List of stock tickers
            period: Time period for all stocks
        
        Returns:
            Dictionary mapping symbol -> DataFrame
        """
        results = {}
        for symbol in symbols:
            try:
                results[symbol] = self.get_stock_data(symbol, period)
            except ValueError as e:
                logger.warning(f"Skipping {symbol}: {e}")
        
        return results
    
    def clear_cache(self, symbol: str = None) -> None:
        """
        Clear cached data.
        
        Args:
            symbol: Specific symbol to clear, or None for all
        """
        if symbol:
            pattern = f"{symbol.upper()}_*.pkl"
        else:
            pattern = "*.pkl"
        
        files_removed = 0
        for cache_file in self.cache_dir.glob(pattern):
            cache_file.unlink()
            files_removed += 1
        
        logger.info(f"Cleared {files_removed} cached files")


# Convenience function for simple usage, I like it yk? 
def get_stock_data(symbol: str, period: str = DEFAULT_PERIOD) -> pd.DataFrame:
    """
    Simple function to get stock data.
    
    This is what most people will use day-to-day.
    The class above gives more control when needed.
    """
    fetcher = DataFetcher()
    return fetcher.get_stock_data(symbol, period)