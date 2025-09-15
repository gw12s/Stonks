"""
Sidebar Component for STONKS Dashboard

Handles all the user input controls:
- Stock selection (with fancy emojis because why not)
- Strategy selection 
- Time periods and settings
- The magic "RUN ANALYSIS" button

Keeps all the sidebar logic in one place so it doesn't clutter the main app.
"""

import streamlit as st
from config import INITIAL_CAPITAL

def render_sidebar():
    """
    Render the sidebar and return analysis configuration.
    
    Returns:
        dict: Configuration for running analysis, or None if not ready
    """
    st.sidebar.header("⚙️ Configuration")
    
    # Stock selection section
    symbols = _render_stock_selection()
    
    # Time period selection
    period = _render_time_period()
    
    # Strategy selection  
    strategies = _render_strategy_selection()
    
    # Analysis settings
    initial_capital, commission = _render_analysis_settings()
    
    # The big red button
    run_analysis = st.sidebar.button("🚀 RUN ANALYSIS", type="primary", use_container_width=True)
    
    if run_analysis:
        return {
            'symbols': symbols,
            'period': period,
            'strategies': strategies,
            'initial_capital': initial_capital,
            'commission': commission,
            'run_analysis': True
        }
    
    return {
        'symbols': symbols,
        'period': period, 
        'strategies': strategies,
        'initial_capital': initial_capital,
        'commission': commission,
        'run_analysis': False
    }

def _render_stock_selection():
    """Render stock selection controls."""
    st.sidebar.subheader("📊 Stock Selection")
    
    # Popular stocks with emojis (because we're fancy)
    popular_stocks = {
        "🍎 Apple (AAPL)": "AAPL",
        "🔍 Google (GOOGL)": "GOOGL", 
        "🪟 Microsoft (MSFT)": "MSFT",
        "⚡ Tesla (TSLA)": "TSLA",
        "🏢 Amazon (AMZN)": "AMZN",
        "📱 Meta (META)": "META",
        "🎥 Netflix (NFLX)": "NFLX",
        "📈 S&P 500 (SPY)": "SPY",
        "💎 Nasdaq (QQQ)": "QQQ",
        "💰 Bitcoin (BTC-USD)": "BTC-USD"
    }
    
    selected_stocks = st.sidebar.multiselect(
        "Choose stocks to analyze:",
        options=list(popular_stocks.keys()),
        default=["🍎 Apple (AAPL)", "📈 S&P 500 (SPY)"],
        max_selections=3,
        help="Select up to 3 stocks for analysis"
    )
    
    # Convert display names to symbols
    symbols = [popular_stocks[stock] for stock in selected_stocks]
    
    # Custom symbol input
    st.sidebar.markdown("**Or add custom symbol:**")
    custom_symbol = st.sidebar.text_input(
        "Enter symbol:",
        placeholder="e.g., NVDA, GME, DOGE-USD",
        help="Any valid Yahoo Finance symbol"
    ).upper().strip()
    
    if custom_symbol and custom_symbol not in symbols:
        symbols.append(custom_symbol)
        if len(symbols) > 3:
            st.sidebar.warning("⚠️ Too many symbols! Using first 3.")
            symbols = symbols[:3]
    
    # Show selected symbols
    if symbols:
        st.sidebar.success(f"Selected: {', '.join(symbols)}")
    
    return symbols

def _render_time_period():
    """Render time period selection."""
    st.sidebar.subheader("📅 Time Period")
    
    period_options = {
        "1 Month": "1mo",
        "3 Months": "3mo", 
        "6 Months": "6mo",
        "1 Year": "1y",
        "2 Years": "2y",
        "5 Years": "5y"
    }
    
    selected_period = st.sidebar.selectbox(
        "Analysis period:",
        options=list(period_options.keys()),
        index=3,  # Default to 1 year
        help="Longer periods = more data, but older strategies might not be relevant"
    )
    
    return period_options[selected_period]

def _render_strategy_selection():
    """Render strategy selection controls."""
    st.sidebar.subheader("🎯 Strategy Selection")
    
    # Available strategies (we'll add more later)
    available_strategies = {
        "MA Cross (50/200) - Golden Cross": {
            "type": "ma",
            "params": {"short": 50, "long": 200},
            "description": "Classic long-term trend following"
        },
        "MA Cross (20/50) - Medium Term": {
            "type": "ma", 
            "params": {"short": 20, "long": 50},
            "description": "More responsive to price changes"
        },
        "MA Cross (10/30) - Short Term": {
            "type": "ma",
            "params": {"short": 10, "long": 30}, 
            "description": "Quick signals, more trades"
        },
    }
    
    selected_strategy_names = st.sidebar.multiselect(
        "Choose strategies (max 3):",
        options=list(available_strategies.keys()),
        default=["MA Cross (50/200) - Golden Cross"],
        max_selections=3,
        help="Test multiple strategies to see which performs best"
    )
    
    # Convert to strategy configs
    strategies = []
    for name in selected_strategy_names:
        config = available_strategies[name].copy()
        config['name'] = name
        strategies.append(config)
    
    # Show strategy descriptions
    if strategies:
        st.sidebar.markdown("**Selected Strategies:**")
        for strategy in strategies:
            with st.sidebar.expander(strategy['name']):
                st.write(strategy['description'])
                if strategy['type'] == 'ma':
                    params = strategy['params']
                    st.write(f"• Short MA: {params['short']} days")
                    st.write(f"• Long MA: {params['long']} days")
    
    return strategies

def _render_analysis_settings():
    """Render analysis settings (capital, commission, etc)."""
    st.sidebar.subheader("💰 Analysis Settings")
    
    # Initial capital
    initial_capital = st.sidebar.number_input(
        "Initial Capital ($):",
        min_value=1000,
        max_value=10000000,
        value=INITIAL_CAPITAL,
        step=1000,
        help="Starting amount for backtesting"
    )
    
    # Commission
    commission_pct = st.sidebar.slider(
        "Commission (%):",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.05,
        format="%.2f%%",
        help="Trading costs per transaction"
    )
    
    commission = commission_pct / 100
    
    # Show what this means
    example_trade = initial_capital * 0.1  # 10% position
    commission_cost = example_trade * commission
    
    st.sidebar.caption(
        f"💡 Example: ${example_trade:,.0f} trade = ${commission_cost:.2f} commission"
    )
    
    return initial_capital, commission