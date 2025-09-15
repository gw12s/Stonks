"""
   📈 STONKS STRATEGY BASE CLASS 📈
   
Base class for all trading strategies.

Because we're fancy and use inheritance like real software engineers.
Also because copy-pasting code is for peasants.

All strategies must implement:
- generate_signals(): Figure out when to buy/sell
- backtest(): See how badly we would have lost money
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime

from utils.logger import setup_logger
from config import INITIAL_CAPITAL

logger = setup_logger(__name__)


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    Why abstract base class?
    - Forces all strategies to implement required methods
    - Provides common functionality (backtesting, metrics)
    - Makes code consistent and maintainable
    - Sounds smart in interviews
    """
    
    def __init__(self, name: str = "Mystery Strategy"):
        """
        Initialize the strategy.
        
        Args:
            name: Human-readable name for this strategy
        """
        self.name = name
        self.signals = None
        self.backtest_results = None
        logger.info(f"Initialized strategy: {self.name}")
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy/sell signals based on price data.
        
        This is the heart of your strategy - where the magic happens!
        (Or where dreams go to die)
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with additional columns:
            - 'Signal': 1 for buy, -1 for sell, 0 for hold
            - 'Position': Current position (1=long, 0=flat, -1=short)
        """
        pass
    
    def backtest(
        self, 
        data: pd.DataFrame, 
        initial_capital: float = INITIAL_CAPITAL,
        commission: float = 0.001  # 0.1% per trade
    ) -> Dict[str, Any]:
        """
        Backtest the strategy on historical data.
        
        Args:
            data: Historical price data
            initial_capital: Starting money
            commission: Trading costs as fraction (0.001 = 0.1%)
            
        Returns:
            Dictionary with performance metrics
        """
        logger.info(f"Backtesting {self.name} with ${initial_capital:,.2f}")
        
        # Generate signals
        data_with_signals = self.generate_signals(data.copy())
        
        # Calculate returns
        results = self._calculate_returns(
            data_with_signals, 
            initial_capital, 
            commission
        )
        
        # Calculate performance metrics
        metrics = self._calculate_metrics(data_with_signals, results)
        
        # Store results
        self.backtest_results = {
            'data': data_with_signals,
            'equity_curve': results,
            'metrics': metrics,
            'initial_capital': initial_capital,
            'commission': commission
        }
        
        logger.info(f"Backtest complete. Final return: {metrics['total_return']:.2%}")
        return self.backtest_results
    
    def _calculate_returns(
        self, 
        data: pd.DataFrame, 
        initial_capital: float,
        commission: float
    ) -> pd.DataFrame:
        """
        Calculate portfolio returns based on signals.
        
        This is where we find out how much money we would have made/lost.
        Spoiler: Usually lost.
        """
        # Calculate daily returns
        data['Returns'] = data['Close'].pct_change()
        
        # Shift signals to avoid look-ahead bias
        # (Can't buy at today's close based on today's signal)
        data['Position_Lagged'] = data['Position'].shift(1).fillna(0)
        
        # Strategy returns = position * market returns
        data['Strategy_Returns'] = data['Position_Lagged'] * data['Returns']
        
        # Apply commission costs when position changes
        data['Position_Change'] = data['Position_Lagged'].diff().abs()
        data['Commission_Cost'] = data['Position_Change'] * commission
        data['Strategy_Returns_Net'] = data['Strategy_Returns'] - data['Commission_Cost']
        
        # Calculate cumulative returns and equity curve
        data['Cumulative_Returns'] = (1 + data['Strategy_Returns_Net']).cumprod()
        data['Portfolio_Value'] = initial_capital * data['Cumulative_Returns']
        
        # Buy and hold comparison
        data['BuyHold_Returns'] = data['Returns'].fillna(0)
        data['BuyHold_Cumulative'] = (1 + data['BuyHold_Returns']).cumprod()
        data['BuyHold_Value'] = initial_capital * data['BuyHold_Cumulative']
        
        return data
    
    def _calculate_metrics(self, data: pd.DataFrame, results: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate performance metrics.
        
        All the numbers that tell you how badly you failed.
        Or succeeded! (But probably failed)
        """
        strategy_returns = results['Strategy_Returns_Net'].dropna()
        buyhold_returns = results['BuyHold_Returns'].dropna()
        
        # Basic returns
        total_return = results['Cumulative_Returns'].iloc[-1] - 1
        buyhold_return = results['BuyHold_Cumulative'].iloc[-1] - 1
        
        # Risk metrics
        volatility = strategy_returns.std() * np.sqrt(252)  # Annualized
        max_drawdown = self._calculate_max_drawdown(results['Portfolio_Value'])
        
        # Risk-adjusted returns
        sharpe_ratio = self._calculate_sharpe_ratio(strategy_returns)
        
        # Win rate
        winning_trades = (strategy_returns > 0).sum()
        total_trades = len(strategy_returns[strategy_returns != 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        return {
            'total_return': total_return,
            'buyhold_return': buyhold_return,
            'excess_return': total_return - buyhold_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': total_trades
        }
    
    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown from peak."""
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        return drawdown.min()
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio (risk-adjusted return)."""
        if returns.std() == 0:
            return 0
        
        excess_return = returns.mean() * 252 - risk_free_rate  # Annualized
        volatility = returns.std() * np.sqrt(252)
        
        return excess_return / volatility
    
    def print_results(self) -> None:
        """
        Print backtest results in a nice format.
        
        Because nobody likes ugly output.
        """
        if self.backtest_results is None:
            print("❌ No backtest results available. Run backtest() first!")
            return
        
        metrics = self.backtest_results['metrics']
        
        print(f"\n📊 {self.name} Results:")
        print("=" * 50)
        print(f"💰 Total Return:     {metrics['total_return']:>8.2%}")
        print(f"📈 Buy & Hold:       {metrics['buyhold_return']:>8.2%}")
        print(f"🎯 Excess Return:    {metrics['excess_return']:>8.2%}")
        print(f"📉 Max Drawdown:     {metrics['max_drawdown']:>8.2%}")
        print(f"⚡ Sharpe Ratio:     {metrics['sharpe_ratio']:>8.2f}")
        print(f"🎲 Win Rate:         {metrics['win_rate']:>8.2%}")
        print(f"🔄 Total Trades:     {metrics['total_trades']:>8.0f}")
        
        # Verdict
        if metrics['excess_return'] > 0:
            print(f"\n🎉 Strategy beats buy & hold by {metrics['excess_return']:.2%}!")
        else:
            print(f"\n😭 Strategy underperforms by {abs(metrics['excess_return']):.2%}")
            print("   Maybe just buy index funds? 🤷‍♂️")