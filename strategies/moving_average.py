"""
Moving Average Crossover Strategy 📈

The most basic strategy in existence:
- Buy when short MA crosses above long MA
- Sell when short MA crosses below long MA
- Hope for the best

This strategy is older than the internet and about as reliable.
But hey, at least it's simple!
"""

import pandas as pd
import numpy as np
from typing import Optional

from strategies.base_strategy import BaseStrategy
from utils.logger import setup_logger
from config import DEFAULT_SHORT_WINDOW, DEFAULT_LONG_WINDOW

logger = setup_logger(__name__)


class MovingAverageStrategy(BaseStrategy):
    """
    Simple moving average crossover strategy.
    
    Strategy Logic:
    1. Calculate short-term MA (e.g., 50 days)
    2. Calculate long-term MA (e.g., 200 days)  
    3. Buy when short MA > long MA (golden cross)
    4. Sell when short MA < long MA (death cross)
    
    Fun fact: This strategy worked great in the 80s and 90s.
    These days? Well, everyone knows about it now...
    """
    
    def __init__(
        self, 
        short_window: int = DEFAULT_SHORT_WINDOW,
        long_window: int = DEFAULT_LONG_WINDOW,
        name: Optional[str] = None
    ):
        """
        Initialize the MA crossover strategy.
        
        Args:
            short_window: Days for short-term moving average
            long_window: Days for long-term moving average  
            name: Custom name for this strategy
        """
        if name is None:
            name = f"MA Crossover ({short_window}/{long_window})"
        
        super().__init__(name)
        
        self.short_window = short_window
        self.long_window = long_window
        
        # Validation (because users do silly things)
        if short_window >= long_window:
            raise ValueError(f"Short window ({short_window}) must be less than long window ({long_window})")
        
        if short_window < 2:
            raise ValueError("Short window must be at least 2 days")
            
        logger.info(f"MA Strategy: {short_window}-day vs {long_window}-day crossover")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy/sell signals based on MA crossover.
        
        Args:
            data: DataFrame with at least 'Close' column
            
        Returns:
            DataFrame with additional signal columns
        """
        if len(data) < self.long_window:
            logger.warning(f"Not enough data ({len(data)} days) for {self.long_window}-day MA")
            # Return data with zero signals
            data['Signal'] = 0
            data['Position'] = 0
            return data
        
        # Calculate moving averages
        data[f'MA_{self.short_window}'] = data['Close'].rolling(
            window=self.short_window,
            min_periods=self.short_window
        ).mean()
        
        data[f'MA_{self.long_window}'] = data['Close'].rolling(
            window=self.long_window,
            min_periods=self.long_window
        ).mean()
        
        # Generate signals
        # 1 = Buy, -1 = Sell, 0 = Hold
        data['Signal'] = 0
        
        # Golden Cross: Short MA crosses above Long MA -> BUY
        golden_cross = (
            (data[f'MA_{self.short_window}'] > data[f'MA_{self.long_window}']) &
            (data[f'MA_{self.short_window}'].shift(1) <= data[f'MA_{self.long_window}'].shift(1))
        )
        data.loc[golden_cross, 'Signal'] = 1
        
        # Death Cross: Short MA crosses below Long MA -> SELL  
        death_cross = (
            (data[f'MA_{self.short_window}'] < data[f'MA_{self.long_window}']) &
            (data[f'MA_{self.short_window}'].shift(1) >= data[f'MA_{self.long_window}'].shift(1))
        )
        data.loc[death_cross, 'Signal'] = -1
        
        # Convert signals to positions
        # Position represents what we should hold: 1=long, 0=cash, -1=short
        data['Position'] = 0
        
        current_position = 0
        for i in range(len(data)):
            if data.iloc[i]['Signal'] == 1:  # Buy signal
                current_position = 1
            elif data.iloc[i]['Signal'] == -1:  # Sell signal  
                current_position = 0  # Go to cash (no shorting for now)
            
            data.iloc[i, data.columns.get_loc('Position')] = current_position
        
        # Add some diagnostic info
        total_signals = (data['Signal'] != 0).sum()
        buy_signals = (data['Signal'] == 1).sum()
        sell_signals = (data['Signal'] == -1).sum()
        
        logger.info(f"Generated {total_signals} total signals ({buy_signals} buy, {sell_signals} sell)")
        
        return data
    
    def plot_signals(self, figsize: tuple = (15, 8)) -> None:
        """
        Plot price data with moving averages and signals.
        
        Because a picture is worth a thousand backtest results.
        """
        if self.backtest_results is None:
            print("❌ No backtest results to plot. Run backtest() first!")
            return
        
        try:
            import matplotlib.pyplot as plt
            
            data = self.backtest_results['data']
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, height_ratios=[3, 1])
            
            # Price and moving averages
            ax1.plot(data.index, data['Close'], label='Close Price', linewidth=1, color='black')
            ax1.plot(data.index, data[f'MA_{self.short_window}'], 
                    label=f'{self.short_window}-day MA', linewidth=1, color='blue')
            ax1.plot(data.index, data[f'MA_{self.long_window}'], 
                    label=f'{self.long_window}-day MA', linewidth=1, color='red')
            
            # Buy/sell signals
            buy_signals = data[data['Signal'] == 1]
            sell_signals = data[data['Signal'] == -1]
            
            ax1.scatter(buy_signals.index, buy_signals['Close'], 
                       marker='^', color='green', s=100, label='Buy', zorder=5)
            ax1.scatter(sell_signals.index, sell_signals['Close'], 
                       marker='v', color='red', s=100, label='Sell', zorder=5)
            
            ax1.set_title(f'{self.name} - Price and Signals')
            ax1.set_ylabel('Price ($)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Portfolio value vs buy & hold
            ax2.plot(data.index, data['Portfolio_Value'], 
                    label='Strategy', linewidth=2, color='green')
            ax2.plot(data.index, data['BuyHold_Value'], 
                    label='Buy & Hold', linewidth=2, color='blue')
            
            ax2.set_title('Portfolio Value Comparison')
            ax2.set_ylabel('Portfolio Value ($)')
            ax2.set_xlabel('Date')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            print("❌ Matplotlib not installed. Install with: pip install matplotlib")
        except Exception as e:
            logger.error(f"Plotting failed: {e}")
            print(f"❌ Plotting failed: {e}")


# Convenience function for quick testing
def test_ma_strategy(symbol: str = "AAPL", period: str = "2y") -> MovingAverageStrategy:
    """
    Quick test of the MA strategy.
    
    Because sometimes you just want to see if your strategy works
    without writing a whole test script.
    """
    from utils.data_fetcher import get_stock_data
    
    print(f"🧪 Testing MA strategy on {symbol} ({period})")
    
    # Get data
    data = get_stock_data(symbol, period)
    
    # Create and test strategy
    strategy = MovingAverageStrategy(50, 200)
    results = strategy.backtest(data)
    
    # Print results
    strategy.print_results()
    
    return strategy