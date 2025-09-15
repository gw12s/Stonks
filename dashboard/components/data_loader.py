"""
Data Loading Component

Handles all data fetching with caching for the dashboard.
Because nobody wants to wait 30 seconds every time they change a setting.

This component:
- Uses Streamlit's caching to avoid repeated API calls
- Provides error handling for bad symbols
- Shows sample data when the app first loads
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

from utils.data_fetcher import get_stock_data
from utils.logger import setup_logger

logger = setup_logger(__name__)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_and_cache_data(symbol: str, period: str) -> pd.DataFrame:
    """
    Load stock data with Streamlit caching.
    
    Args:
        symbol: Stock ticker symbol
        period: Time period (1mo, 3mo, 6mo, 1y, 2y, 5y)
    
    Returns:
        DataFrame with stock data, or empty DataFrame if failed
    """
    try:
        logger.info(f"Loading data for {symbol} ({period})")
        data = get_stock_data(symbol, period)
        
        if data.empty:
            logger.warning(f"No data returned for {symbol}")
            return pd.DataFrame()
        
        logger.info(f"Successfully loaded {len(data)} rows for {symbol}")
        return data
        
    except Exception as e:
        logger.error(f"Failed to load data for {symbol}: {e}")
        return pd.DataFrame()

def validate_data(data: pd.DataFrame, symbol: str) -> bool:
    """
    Validate that we have usable data.
    
    Args:
        data: Stock data DataFrame
        symbol: Symbol name for error messages
    
    Returns:
        True if data is valid, False otherwise
    """
    if data.empty:
        st.error(f"❌ No data found for {symbol}. Check symbol spelling.")
        return False
    
    if len(data) < 50:
        st.warning(f"⚠️ Limited data for {symbol} ({len(data)} days). Results may be unreliable.")
    
    # Check for required columns
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing_cols = [col for col in required_cols if col not in data.columns]
    
    if missing_cols:
        st.error(f"❌ Missing data columns for {symbol}: {missing_cols}")
        return False
    
    return True

def load_sample_chart():
    """Load and display a sample chart for the welcome screen."""
    try:
        # Load SPY data for the last month
        sample_data = load_and_cache_data("SPY", "1mo")
        
        if not sample_data.empty:
            st.subheader("📊 Sample: SPY (S&P 500) - Last 30 Days")
            
            # Create a simple price chart
            fig = px.line(
                sample_data.reset_index(),
                x='Date',
                y='Close', 
                title="S&P 500 Price Movement",
                labels={'Close': 'Price ($)', 'Date': 'Date'}
            )
            
            fig.update_layout(
                height=400,
                showlegend=False,
                hovermode='x unified'
            )
            
            # Add some styling
            fig.update_traces(line_color='#1f77b4', line_width=2)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show some basic stats
            latest_price = sample_data['Close'].iloc[-1]
            first_price = sample_data['Close'].iloc[0]
            month_return = (latest_price - first_price) / first_price
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Price", f"${latest_price:.2f}")
            with col2:
                st.metric("30-Day Return", f"{month_return:.2%}")
            with col3:
                st.metric("Data Points", f"{len(sample_data)}")
                
        else:
            st.info("Sample chart unavailable. Select stocks and run analysis to see charts!")
            
    except Exception as e:
        logger.debug(f"Could not load sample chart: {e}")
        st.info("💡 Select stocks from the sidebar and click 'RUN ANALYSIS' to see interactive charts!")

@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_symbol_info(symbol: str) -> dict:
    """
    Get basic info about a stock symbol.
    
    Args:
        symbol: Stock ticker
        
    Returns:
        Dict with basic symbol info, or empty dict if unavailable
    """
    try:
        # This is a placeholder - could be enhanced with yfinance Ticker info
        # For now, just return basic validation
        data = load_and_cache_data(symbol, "5d")  # Just get a few days
        
        if not data.empty:
            latest = data.iloc[-1]
            return {
                'symbol': symbol,
                'latest_price': latest['Close'],
                'valid': True
            }
        else:
            return {'symbol': symbol, 'valid': False}
            
    except Exception as e:
        logger.debug(f"Could not get info for {symbol}: {e}")
        return {'symbol': symbol, 'valid': False}

def check_data_quality(data: pd.DataFrame, symbol: str) -> dict:
    """
    Analyze data quality and return a report.
    
    Args:
        data: Stock data DataFrame
        symbol: Symbol for reporting
        
    Returns:
        Dict with quality metrics
    """
    if data.empty:
        return {'quality_score': 0, 'issues': ['No data available']}
    
    issues = []
    quality_score = 100
    
    # Check for missing data
    missing_pct = data.isnull().sum().sum() / (len(data) * len(data.columns))
    if missing_pct > 0.05:  # More than 5% missing
        issues.append(f"High missing data: {missing_pct:.1%}")
        quality_score -= 20
    
    # Check for price anomalies
    returns = data['Close'].pct_change().dropna()
    extreme_moves = (abs(returns) > 0.2).sum()  # >20% daily moves
    if extreme_moves > len(returns) * 0.01:  # More than 1% of days
        issues.append(f"Unusual price volatility detected")
        quality_score -= 15
    
    # Check data recency
    if hasattr(data.index, 'max'):
        latest_date = data.index.max()
        days_old = (datetime.now() - latest_date).days
        if days_old > 7:
            issues.append(f"Data is {days_old} days old")
            quality_score -= 10
    
    # Check volume (if available)
    if 'Volume' in data.columns:
        zero_volume_days = (data['Volume'] == 0).sum()
        if zero_volume_days > len(data) * 0.1:  # More than 10% zero volume
            issues.append("Many zero-volume days (illiquid)")
            quality_score -= 10
    
    return {
        'quality_score': max(0, quality_score),
        'issues': issues,
        'data_points': len(data),
        'date_range': f"{data.index.min().strftime('%Y-%m-%d')} to {data.index.max().strftime('%Y-%m-%d')}"
    }