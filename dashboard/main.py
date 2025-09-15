"""
Main Streamlit Dashboard Application

Clean, modular dashboard that doesn't make your eyes bleed.
Separated concerns like a proper engineer.
"""

import streamlit as st
from datetime import datetime

from dashboard.components.sidebar import render_sidebar
from dashboard.components.data_loader import load_and_cache_data
from dashboard.components.charts import create_strategy_charts
from dashboard.components.metrics import display_performance_summary
from utils.logger import setup_logger
from config import PAGE_TITLE, PAGE_ICON

logger = setup_logger(__name__)

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

def apply_custom_css():
    """Apply custom CSS styling."""
    st.markdown("""
    <style>
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #ff6b6b;
            margin: 0.5rem 0;
        }
        .success-metric { border-left-color: #51cf66; }
        .warning-metric { border-left-color: #ffd43b; }
        .error-metric { border-left-color: #ff6b6b; }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding-left: 20px;
            padding-right: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Render the main header."""
    st.title("📈 STONKS Dashboard")
    st.markdown("""
    *Professional-grade stock analysis for the discerning retail investor*
    
    **What this does:** Tests trading strategies against historical data to see if you could have beaten buy-and-hold  
    **What this doesn't do:** Predict the future or guarantee profits
    """)

def render_welcome_screen():
    """Render welcome screen when no analysis is running."""
    st.info("""
    👋 **Welcome to the STONKS Dashboard!**
    
    **Quick Start:**
    1. 📊 Select stocks from the sidebar (or enter custom symbols)
    2. 📅 Choose your analysis period  
    3. 🎯 Pick strategies to test (up to 3)
    4. 🚀 Click "RUN ANALYSIS" and watch the magic happen!
    
    **Pro Tips:**
    - Start with SPY (S&P 500) to benchmark against the market
    - Try different MA crossover periods to see what works
    - Remember: past performance ≠ future results!
    """)
    
    # Show sample chart if possible
    try:
        from dashboard.components.data_loader import load_sample_chart
        load_sample_chart()
    except Exception as e:
        logger.debug(f"Could not load sample chart: {e}")

def render_analysis_results(analysis_config, all_results):
    """Render the analysis results."""
    st.header("📊 Analysis Results")
    
    # Performance summary table
    display_performance_summary(all_results)
    
    # Detailed charts for each stock
    for symbol, strategies in all_results.items():
        st.header(f"📈 {symbol} Analysis")
        
        # Create tabs for each strategy
        if strategies:
            strategy_names = list(strategies.keys())
            tabs = st.tabs(strategy_names)
            
            for tab, (strategy_name, result) in zip(tabs, strategies.items()):
                with tab:
                    create_strategy_charts(symbol, strategy_name, result, analysis_config)

def run_analysis(analysis_config):
    """Run the strategy analysis."""
    symbols = analysis_config['symbols']
    strategies = analysis_config['strategies']
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_tasks = len(symbols) * len(strategies)
    completed_tasks = 0
    
    all_results = {}
    
    for symbol in symbols:
        status_text.text(f"📊 Loading data for {symbol}...")
        
        try:
            # Load data
            data = load_and_cache_data(symbol, analysis_config['period'])
            
            if data.empty:
                st.error(f"❌ No data found for {symbol}")
                continue
            
            all_results[symbol] = {}
            
            # Run each strategy
            for strategy_config in strategies:
                strategy_name = strategy_config['name']
                status_text.text(f"🎯 Running {strategy_name} on {symbol}...")
                
                try:
                    # Import and run strategy
                    from strategies.moving_average import MovingAverageStrategy
                    
                    if strategy_config['type'] == 'ma':
                        params = strategy_config['params']
                        strategy = MovingAverageStrategy(
                            short_window=params['short'],
                            long_window=params['long'],
                            name=strategy_name
                        )
                        
                        results = strategy.backtest(
                            data.copy(),
                            initial_capital=analysis_config['initial_capital'],
                            commission=analysis_config['commission']
                        )
                        
                        all_results[symbol][strategy_name] = {
                            'strategy': strategy,
                            'results': results,
                            'data': data
                        }
                
                except Exception as e:
                    st.error(f"❌ Error running {strategy_name} on {symbol}: {e}")
                    logger.error(f"Strategy error: {e}")
                
                completed_tasks += 1
                progress_bar.progress(completed_tasks / total_tasks)
        
        except Exception as e:
            st.error(f"❌ Error loading data for {symbol}: {e}")
            logger.error(f"Data loading error: {e}")
    
    # Clean up progress indicators
    progress_bar.empty()
    status_text.empty()
    
    return all_results

def run_dashboard():
    """Main dashboard function."""
    apply_custom_css()
    render_header()
    
    # Render sidebar and get configuration
    analysis_config = render_sidebar()
    
    # Main content area
    if analysis_config and analysis_config.get('run_analysis'):
        # Validate inputs
        if not analysis_config['symbols']:
            st.warning("⚠️ Please select at least one stock to analyze.")
            return
        
        if not analysis_config['strategies']:
            st.warning("⚠️ Please select at least one strategy.")
            return
        
        # Run analysis
        with st.spinner("🚀 Running analysis..."):
            all_results = run_analysis(analysis_config)
        
        if all_results:
            render_analysis_results(analysis_config, all_results)
        else:
            st.error("❌ No results generated. Please check your inputs and try again.")
    
    else:
        render_welcome_screen()

if __name__ == "__main__":
    run_dashboard()