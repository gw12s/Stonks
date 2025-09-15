"""
Charts Component for STONKS Dashboard

Creates all the beautiful interactive charts that make people go "ooh" and "ahh".

This handles:
- Price charts with moving averages
- Buy/sell signal visualization  
- Portfolio performance comparison
- Download functionality

Because static charts are for peasants.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime

from dashboard.components.metrics import display_strategy_metrics
from utils.logger import setup_logger

logger = setup_logger(__name__)

def create_strategy_charts(symbol: str, strategy_name: str, result: dict, analysis_config: dict):
    """
    Create all charts and displays for a single strategy result.
    
    Args:
        symbol: Stock symbol
        strategy_name: Name of the strategy
        result: Strategy results dictionary
        analysis_config: Analysis configuration
    """
    
    # Display performance metrics first
    display_strategy_metrics(result['results'], strategy_name)
    
    # Create main price chart
    price_chart = create_price_and_signals_chart(symbol, strategy_name, result)
    st.plotly_chart(price_chart, use_container_width=True)
    
    # Additional analysis charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Returns distribution
        returns_chart = create_returns_distribution_chart(result)
        st.plotly_chart(returns_chart, use_container_width=True)
    
    with col2:
        # Drawdown chart
        drawdown_chart = create_drawdown_chart(result)
        st.plotly_chart(drawdown_chart, use_container_width=True)
    
    # Data export section
    create_export_section(symbol, strategy_name, result, analysis_config)

def create_price_and_signals_chart(symbol: str, strategy_name: str, result: dict):
    """Create the main price chart with signals and moving averages."""
    
    strategy_data = result['results']['data']
    
    # Create subplots: price chart on top, portfolio value on bottom
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(
            f'{symbol} - {strategy_name}',
            'Portfolio Value Comparison'
        ),
        row_heights=[0.7, 0.3]
    )
    
    # Price line
    fig.add_trace(
        go.Scatter(
            x=strategy_data.index,
            y=strategy_data['Close'],
            name='Close Price',
            line=dict(color='black', width=1.5),
            hovertemplate='%{x}<br>Price: $%{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Moving averages (detect which ones exist)
    ma_columns = [col for col in strategy_data.columns if col.startswith('MA_')]
    colors = ['blue', 'red', 'orange', 'purple']
    
    for i, ma_col in enumerate(ma_columns):
        period = ma_col.split('_')[1]
        fig.add_trace(
            go.Scatter(
                x=strategy_data.index,
                y=strategy_data[ma_col],
                name=f'{period}-day MA',
                line=dict(color=colors[i % len(colors)], width=1),
                hovertemplate=f'%{{x}}<br>{period}-day MA: $%{{y:.2f}}<extra></extra>'
            ),
            row=1, col=1
        )
    
    # Buy signals
    buy_signals = strategy_data[strategy_data['Signal'] == 1]
    if not buy_signals.empty:
        fig.add_trace(
            go.Scatter(
                x=buy_signals.index,
                y=buy_signals['Close'],
                mode='markers',
                name='Buy Signal',
                marker=dict(
                    symbol='triangle-up',
                    size=12,
                    color='green',
                    line=dict(color='darkgreen', width=1)
                ),
                hovertemplate='%{x}<br>BUY: $%{y:.2f}<extra></extra>'
            ),
            row=1, col=1
        )
    
    # Sell signals
    sell_signals = strategy_data[strategy_data['Signal'] == -1]
    if not sell_signals.empty:
        fig.add_trace(
            go.Scatter(
                x=sell_signals.index,
                y=sell_signals['Close'],
                mode='markers',
                name='Sell Signal',
                marker=dict(
                    symbol='triangle-down',
                    size=12,
                    color='red',
                    line=dict(color='darkred', width=1)
                ),
                hovertemplate='%{x}<br>SELL: $%{y:.2f}<extra></extra>'
            ),
            row=1, col=1
        )
    
    # Portfolio value comparison
    fig.add_trace(
        go.Scatter(
            x=strategy_data.index,
            y=strategy_data['Portfolio_Value'],
            name='Strategy',
            line=dict(color='green', width=2),
            hovertemplate='%{x}<br>Strategy: $%{y:,.0f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=strategy_data.index,
            y=strategy_data['BuyHold_Value'],
            name='Buy & Hold',
            line=dict(color='blue', width=2),
            hovertemplate='%{x}<br>Buy & Hold: $%{y:,.0f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        height=700,
        showlegend=True,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Portfolio Value ($)", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    
    return fig

def create_returns_distribution_chart(result: dict):
    """Create a histogram of daily returns."""
    
    strategy_data = result['results']['data']
    returns = strategy_data['Strategy_Returns_Net'].dropna()
    
    fig = px.histogram(
        x=returns,
        nbins=30,
        title="Daily Returns Distribution",
        labels={'x': 'Daily Return', 'y': 'Frequency'},
        color_discrete_sequence=['lightblue']
    )
    
    # Add vertical line at 0
    fig.add_vline(x=0, line_dash="dash", line_color="red", 
                  annotation_text="Break-even")
    
    # Add mean line
    mean_return = returns.mean()
    fig.add_vline(x=mean_return, line_dash="dot", line_color="green",
                  annotation_text=f"Mean: {mean_return:.3f}")
    
    fig.update_layout(height=300, showlegend=False)
    
    return fig

def create_drawdown_chart(result: dict):
    """Create a drawdown chart showing peak-to-trough declines."""
    
    strategy_data = result['results']['data']
    portfolio_value = strategy_data['Portfolio_Value']
    
    # Calculate drawdown
    peak = portfolio_value.expanding().max()
    drawdown = (portfolio_value - peak) / peak
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=strategy_data.index,
            y=drawdown * 100,  # Convert to percentage
            fill='tonexty',
            fillcolor='rgba(255, 0, 0, 0.3)',
            line=dict(color='red', width=1),
            name='Drawdown',
            hovertemplate='%{x}<br>Drawdown: %{y:.1f}%<extra></extra>'
        )
    )
    
    # Add horizontal line at 0
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    fig.update_layout(
        title="Portfolio Drawdown",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        height=300,
        showlegend=False
    )
    
    return fig

def create_export_section(symbol: str, strategy_name: str, result: dict, analysis_config: dict):
    """Create data export functionality."""
    
    st.subheader("📥 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download full results
        strategy_data = result['results']['data']
        csv_data = strategy_data.to_csv()
        
        st.download_button(
            label=f"📊 Download Full Data ({symbol})",
            data=csv_data,
            file_name=f"{symbol}_{strategy_name.replace(' ', '_')}_{analysis_config['period']}_full.csv",
            mime="text/csv",
            help="Download complete dataset with signals and indicators"
        )
    
    with col2:
        # Download summary metrics
        metrics = result['results']['metrics']
        
        summary_data = pd.DataFrame([{
            'Symbol': symbol,
            'Strategy': strategy_name,
            'Period': analysis_config['period'],
            'Total_Return': metrics['total_return'],
            'Excess_Return': metrics['excess_return'],
            'Max_Drawdown': metrics['max_drawdown'],
            'Sharpe_Ratio': metrics['sharpe_ratio'],
            'Win_Rate': metrics['win_rate'],
            'Total_Trades': metrics['total_trades'],
            'Analysis_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }])
        
        summary_csv = summary_data.to_csv(index=False)
        
        st.download_button(
            label=f"📋 Download Summary ({symbol})",
            data=summary_csv,
            file_name=f"{symbol}_{strategy_name.replace(' ', '_')}_{analysis_config['period']}_summary.csv",
            mime="text/csv",
            help="Download performance summary metrics"
        )
    
    # Show quick data preview
    with st.expander("👀 Preview Data"):
        st.dataframe(
            strategy_data[['Close', 'Signal', 'Position', 'Portfolio_Value', 'BuyHold_Value']].tail(10),
            use_container_width=True
        )

def create_comparison_chart(all_results: dict):
    """
    Create a chart comparing multiple strategies across stocks.
    
    Args:
        all_results: Dictionary of all analysis results
    """
    
    # Prepare data for comparison
    comparison_data = []
    
    for symbol, strategies in all_results.items():
        for strategy_name, result in strategies.items():
            metrics = result['results']['metrics']
            comparison_data.append({
                'Symbol': symbol,
                'Strategy': strategy_name,
                'Total Return': metrics['total_return'],
                'Excess Return': metrics['excess_return'],
                'Sharpe Ratio': metrics['sharpe_ratio'],
                'Max Drawdown': abs(metrics['max_drawdown'])  # Make positive for display
            })
    
    if not comparison_data:
        return None
    
    df = pd.DataFrame(comparison_data)
    
    # Create scatter plot: Return vs Risk
    fig = px.scatter(
        df,
        x='Max Drawdown',
        y='Total Return',
        color='Strategy',
        symbol='Symbol',
        size='Sharpe Ratio',
        hover_data=['Excess Return'],
        title='Risk vs Return by Strategy',
        labels={
            'Max Drawdown': 'Max Drawdown (%)',
            'Total Return': 'Total Return (%)'
        }
    )
    
    # Add quadrant lines
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=df['Max Drawdown'].median(), line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(height=500)
    
    return fig