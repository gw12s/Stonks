"""
Metrics Component for STONKS Dashboard

Displays all the fancy performance metrics that make your strategy look professional.
Even if it's losing money, at least it'll look good doing it!

This handles:
- Strategy performance cards with color coding
- Summary tables comparing multiple strategies  
- Risk metrics and ratios
- Win/loss statistics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def format_metric_card(title: str, value: str, delta: str = None, card_type: str = "default"):
    """
    Create a styled metric card with color coding.
    
    Args:
        title: Metric name
        value: Main value to display
        delta: Optional change/comparison value
        card_type: Type for color coding (success, warning, error, default)
    """
    
    # Color coding based on card type
    colors = {
        "success": "#d4edda",
        "warning": "#fff3cd", 
        "error": "#f8d7da",
        "default": "#f0f2f6"
    }
    
    border_colors = {
        "success": "#51cf66",
        "warning": "#ffd43b",
        "error": "#ff6b6b", 
        "default": "#dee2e6"
    }
    
    bg_color = colors.get(card_type, colors["default"])
    border_color = border_colors.get(card_type, border_colors["default"])
    
    delta_html = ""
    if delta:
        delta_color = "#28a745" if delta.startswith("+") else "#dc3545" if delta.startswith("-") else "#6c757d"
        delta_html = f'<p style="color: {delta_color}; margin: 0; font-size: 14px;">{delta}</p>'
    
    return f"""
    <div style="
        background-color: {bg_color};
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid {border_color};
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    ">
        <h4 style="margin: 0; color: #495057; font-size: 14px;">{title}</h4>
        <p style="margin: 0; font-size: 24px; font-weight: bold; color: #212529;">{value}</p>
        {delta_html}
    </div>
    """

def display_strategy_metrics(strategy_results: dict, strategy_name: str):
    """
    Display comprehensive strategy performance metrics.
    
    Args:
        strategy_results: Results from strategy backtesting
        strategy_name: Name of the strategy
    """
    metrics = strategy_results['metrics']
    
    st.subheader(f"📊 {strategy_name} Performance")
    
    # Top row - Key performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_return = metrics['total_return']
        card_type = "success" if total_return > 0 else "error"
        st.markdown(
            format_metric_card(
                "Total Return", 
                f"{total_return:.2%}",
                card_type=card_type
            ), 
            unsafe_allow_html=True
        )
    
    with col2:
        excess_return = metrics['excess_return']
        card_type = "success" if excess_return > 0 else "error"
        delta = f"vs Buy & Hold"
        st.markdown(
            format_metric_card(
                "Alpha (Excess Return)", 
                f"{excess_return:+.2%}",
                delta=delta,
                card_type=card_type
            ), 
            unsafe_allow_html=True
        )
    
    with col3:
        max_dd = metrics['max_drawdown']
        card_type = "success" if max_dd > -0.1 else "warning" if max_dd > -0.2 else "error"
        st.markdown(
            format_metric_card(
                "Max Drawdown", 
                f"{max_dd:.2%}",
                card_type=card_type
            ), 
            unsafe_allow_html=True
        )
    
    with col4:
        sharpe = metrics['sharpe_ratio']
        if sharpe > 1:
            card_type = "success"
            interpretation = "Excellent"
        elif sharpe > 0.5:
            card_type = "warning" 
            interpretation = "Good"
        elif sharpe > 0:
            card_type = "warning"
            interpretation = "Fair"
        else:
            card_type = "error"
            interpretation = "Poor"
            
        st.markdown(
            format_metric_card(
                "Sharpe Ratio", 
                f"{sharpe:.2f}",
                delta=interpretation,
                card_type=card_type
            ), 
            unsafe_allow_html=True
        )
    
    # Second row - Trading statistics
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        win_rate = metrics['win_rate']
        card_type = "success" if win_rate > 0.6 else "warning" if win_rate > 0.4 else "error"
        st.markdown(
            format_metric_card(
                "Win Rate", 
                f"{win_rate:.1%}",
                card_type=card_type
            ), 
            unsafe_allow_html=True
        )
    
    with col6:
        total_trades = int(metrics['total_trades'])
        # More trades isn't necessarily better, but very few trades might be concerning
        card_type = "warning" if total_trades < 5 else "default"
        st.markdown(
            format_metric_card(
                "Total Trades", 
                f"{total_trades}",
                card_type=card_type
            ), 
            unsafe_allow_html=True
        )
    
    with col7:
        volatility = metrics['volatility']
        card_type = "success" if volatility < 0.2 else "warning" if volatility < 0.4 else "error"
        st.markdown(
            format_metric_card(
                "Annual Volatility", 
                f"{volatility:.1%}",
                card_type=card_type
            ), 
            unsafe_allow_html=True
        )
    
    with col8:
        buyhold_return = metrics['buyhold_return']
        st.markdown(
            format_metric_card(
                "Buy & Hold Return", 
                f"{buyhold_return:.2%}",
                card_type="default"
            ), 
            unsafe_allow_html=True
        )
    
    # Performance interpretation
    _display_performance_interpretation(metrics)

def _display_performance_interpretation(metrics: dict):
    """Display a human-readable interpretation of the results."""
    
    excess_return = metrics['excess_return']
    sharpe_ratio = metrics['sharpe_ratio']
    max_drawdown = metrics['max_drawdown']
    win_rate = metrics['win_rate']
    
    # Overall assessment
    if excess_return > 0.05 and sharpe_ratio > 1 and max_drawdown > -0.15:
        verdict = "🎉 **Excellent Performance!** This strategy significantly outperformed buy-and-hold with good risk management."
        alert_type = "success"
    elif excess_return > 0 and sharpe_ratio > 0.5:
        verdict = "✅ **Good Performance.** Strategy beat buy-and-hold with reasonable risk."
        alert_type = "success"
    elif excess_return > -0.02 and sharpe_ratio > 0:
        verdict = "⚠️ **Mixed Results.** Strategy roughly matched buy-and-hold performance."
        alert_type = "warning"
    else:
        verdict = "❌ **Poor Performance.** Strategy underperformed buy-and-hold. Consider sticking to index funds."
        alert_type = "error"
    
    if alert_type == "success":
        st.success(verdict)
    elif alert_type == "warning":
        st.warning(verdict)
    else:
        st.error(verdict)
    
    # Detailed insights
    insights = []
    
    if sharpe_ratio < 0:
        insights.append("• Negative Sharpe ratio indicates poor risk-adjusted returns")
    elif sharpe_ratio > 1.5:
        insights.append("• Excellent Sharpe ratio - strong risk-adjusted performance")
    
    if max_drawdown < -0.3:
        insights.append("• High drawdown risk - strategy experienced significant losses")
    elif max_drawdown > -0.1:
        insights.append("• Low drawdown - strategy maintained capital well")
    
    if win_rate > 0.7:
        insights.append("• High win rate - strategy picks winners consistently")
    elif win_rate < 0.4:
        insights.append("• Low win rate - many losing trades, but winners might be larger")
    
    if metrics['total_trades'] < 5:
        insights.append("• Few trades generated - strategy may be too conservative")
    elif metrics['total_trades'] > 100:
        insights.append("• High trading frequency - watch out for commission costs")
    
    if insights:
        with st.expander("📝 Detailed Analysis"):
            for insight in insights:
                st.write(insight)

def display_performance_summary(all_results: dict):
    """
    Create a summary table comparing all strategies across all stocks.
    
    Args:
        all_results: Dictionary containing all analysis results
    """
    
    st.subheader("📋 Performance Summary")
    
    # Prepare data for summary table
    summary_data = []
    
    for symbol, strategies in all_results.items():
        for strategy_name, result in strategies.items():
            metrics = result['results']['metrics']
            
            # Determine performance rating
            excess_return = metrics['excess_return']
            if excess_return > 0.05:
                rating = "🏆 Excellent"
            elif excess_return > 0:
                rating = "✅ Good"
            elif excess_return > -0.02:
                rating = "⚠️ Fair"
            else:
                rating = "❌ Poor"
            
            summary_data.append({
                'Stock': symbol,
                'Strategy': strategy_name.replace(' - ', '\n'),  # Line break for display
                'Total Return': f"{metrics['total_return']:.2%}",
                'vs Buy & Hold': f"{metrics['excess_return']:+.2%}",
                'Max Drawdown': f"{metrics['max_drawdown']:.2%}",
                'Sharpe Ratio': f"{metrics['sharpe_ratio']:.2f}",
                'Win Rate': f"{metrics['win_rate']:.1%}",
                'Trades': int(metrics['total_trades']),
                'Rating': rating
            })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        
        # Display the table with custom styling
        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Stock": st.column_config.TextColumn("Stock", width="small"),
                "Strategy": st.column_config.TextColumn("Strategy", width="medium"),
                "Total Return": st.column_config.TextColumn("Total Return", width="small"),
                "vs Buy & Hold": st.column_config.TextColumn("Alpha", width="small"),
                "Max Drawdown": st.column_config.TextColumn("Max DD", width="small"),
                "Sharpe Ratio": st.column_config.TextColumn("Sharpe", width="small"),
                "Win Rate": st.column_config.TextColumn("Win %", width="small"),
                "Trades": st.column_config.NumberColumn("Trades", width="small"),
                "Rating": st.column_config.TextColumn("Rating", width="medium")
            }
        )
        
        # Summary statistics
        _display_summary_statistics(summary_data)
    
    else:
        st.info("No results to summarize yet. Run an analysis to see performance metrics!")

def _display_summary_statistics(summary_data: list):
    """Display aggregate statistics across all strategies."""
    
    if not summary_data:
        return
    
    st.subheader("🎯 Key Insights")
    
    # Calculate aggregates
    total_strategies = len(summary_data)
    profitable_strategies = sum(1 for item in summary_data if '+' in item['vs Buy & Hold'])
    
    # Success rate
    success_rate = profitable_strategies / total_strategies if total_strategies > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Strategies Tested", 
            f"{total_strategies}",
            help="Total number of strategy-stock combinations tested"
        )
    
    with col2:
        st.metric(
            "Beat Buy & Hold", 
            f"{profitable_strategies}",
            delta=f"{success_rate:.1%} success rate",
            help="Number of strategies that outperformed buy-and-hold"
        )
    
    with col3:
        # Find best performing strategy
        best_alpha = -999
        best_combo = "None"
        
        for item in summary_data:
            alpha_str = item['vs Buy & Hold'].replace('+', '').replace('%', '')
            alpha_val = float(alpha_str) / 100
            if alpha_val > best_alpha:
                best_alpha = alpha_val
                best_combo = f"{item['Stock']} - {item['Strategy'].replace(chr(10), ' ')}"
        
        st.metric(
            "Best Performer",
            f"{best_alpha:+.1%}",
            delta=best_combo,
            help="Highest alpha (excess return) achieved"
        )
    
    # Insights based on results
    if success_rate > 0.6:
        st.success("🎉 Great results! Most strategies beat the market.")
    elif success_rate > 0.4:
        st.warning("📊 Mixed results. Some strategies show promise.")
    else:
        st.error("📉 Tough results. Most strategies underperformed. Consider index investing!")

def create_risk_return_scatter(all_results: dict):
    """
    Create a risk-return scatter plot for all strategies.
    
    Args:
        all_results: Dictionary containing all analysis results
        
    Returns:
        Plotly figure object
    """
    
    plot_data = []
    
    for symbol, strategies in all_results.items():
        for strategy_name, result in strategies.items():
            metrics = result['results']['metrics']
            
            plot_data.append({
                'Strategy': strategy_name,
                'Stock': symbol,
                'Total_Return': metrics['total_return'] * 100,  # Convert to percentage
                'Max_Drawdown': abs(metrics['max_drawdown']) * 100,  # Make positive
                'Sharpe_Ratio': metrics['sharpe_ratio'],
                'Combo': f"{symbol} - {strategy_name}"
            })
    
    if not plot_data:
        return None
    
    df = pd.DataFrame(plot_data)
    
    # Create scatter plot
    fig = px.scatter(
        df,
        x='Max_Drawdown',
        y='Total_Return', 
        color='Strategy',
        symbol='Stock',
        size='Sharpe_Ratio',
        hover_name='Combo',
        title='Risk vs Return Analysis',
        labels={
            'Max_Drawdown': 'Maximum Drawdown (%)',
            'Total_Return': 'Total Return (%)',
            'Sharpe_Ratio': 'Sharpe Ratio'
        }
    )
    
    # Add quadrant lines
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, 
                  annotation_text="Break-even line")
    
    median_dd = df['Max_Drawdown'].median()
    fig.add_vline(x=median_dd, line_dash="dash", line_color="gray", opacity=0.5,
                  annotation_text=f"Median Risk: {median_dd:.1f}%")
    
    fig.update_layout(
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig