"""
Quick test to make sure our data fetcher works and explore some real data.

Let's see what the market has been up to! 📈
"""

from utils.data_fetcher import DataFetcher, get_stock_data
import pandas as pd

def explore_stock_data():
    """Quick exploration of stock data."""
    print("🔍 STONKS Data Explorer 🚀\n")
    
    # Test some popular stocks
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "SPY"]
    
    for symbol in symbols:
        try:
            print(f"📊 Fetching {symbol}...")
            data = get_stock_data(symbol, "3mo")  # 3 months of data
            
            latest = data.iloc[-1]
            first = data.iloc[0]
            
            # Calculate simple stats
            total_return = (latest['Close'] - first['Close']) / first['Close']
            volatility = data['Close'].pct_change().std()
            avg_volume = data['Volume'].mean()
            
            print(f"   Latest price: ${latest['Close']:.2f}")
            print(f"   3-month return: {total_return:.2%}")
            print(f"   Daily volatility: {volatility:.2%}")
            print(f"   Avg daily volume: {avg_volume:,.0f}")
            
            # Check if we have the moving averages we added
            if 'SMA_50' in data.columns:
                sma50 = latest['SMA_50']
                if pd.notna(sma50):
                    print(f"   50-day SMA: ${sma50:.2f}")
                    if latest['Close'] > sma50:
                        print("   📈 Above 50-day MA (bullish)")
                    else:
                        print("   📉 Below 50-day MA (bearish)")
            
            print()
            
        except Exception as e:
            print(f"❌ Failed to fetch {symbol}: {e}\n")

def test_caching():
    """Test that our caching system works."""
    print("🧪 Testing cache performance...\n")
    
    import time
    
    # First fetch (should hit API)
    start_time = time.time()
    data1 = get_stock_data("AAPL", "1y")
    first_fetch_time = time.time() - start_time
    
    # Second fetch (should use cache)
    start_time = time.time()
    data2 = get_stock_data("AAPL", "1y")
    second_fetch_time = time.time() - start_time
    
    print(f"First fetch (API): {first_fetch_time:.2f} seconds")
    print(f"Second fetch (cache): {second_fetch_time:.2f} seconds")
    print(f"Cache speedup: {first_fetch_time/second_fetch_time:.1f}x faster")
    
    # Verify data is identical
    if data1.equals(data2):
        print("✅ Cache data matches API data perfectly")
    else:
        print("⚠️  Cache data differs from API data")

def preview_moving_averages():
    """Preview what moving average signals might look like."""
    print("📈 Moving Average Preview...\n")
    
    data = get_stock_data("SPY", "6mo")  # S&P 500 for 6 months
    
    # Calculate different MA periods
    data['MA_20'] = data['Close'].rolling(20).mean()
    data['MA_50'] = data['Close'].rolling(50).mean()
    
    # Look at recent data
    recent = data.tail(10)
    
    print("Recent SPY data with moving averages:")
    print("Date       | Close  | MA_20  | MA_50  | Signal")
    print("-" * 50)
    
    for i, (date, row) in enumerate(recent.iterrows()):
        close = row['Close']
        ma20 = row['MA_20']
        ma50 = row['MA_50']
        
        # Simple signal logic
        if pd.notna(ma20) and pd.notna(ma50):
            if ma20 > ma50:
                signal = "📈 LONG "
            else:
                signal = "📉 SHORT"
        else:
            signal = "⏳ WAIT "
            
        print(f"{date.strftime('%Y-%m-%d')} | ${close:6.2f} | ${ma20:6.2f} | ${ma50:6.2f} | {signal}")

if __name__ == "__main__":
    explore_stock_data()
    test_caching()
    preview_moving_averages()