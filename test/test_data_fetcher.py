"""
Quick test script for the data fetcher.

Run this to make sure everything is working:
python test_data_fetcher.py
"""

from utils.data_fetcher import DataFetcher, get_stock_data
from utils.logger import setup_logger

# Set up logging
logger = setup_logger("test")

def test_basic_fetch():
    """Test basic data fetching."""
    print("🧪 Testing basic data fetch...")
    
    try:
        # Test the simple function
        data = get_stock_data("AAPL", "1mo")
        print(f"✅ Got {len(data)} days of AAPL data")
        print(f"   Latest close: ${data['Close'][-1]:.2f}")
        print(f"   Columns: {list(data.columns)}")
        
    except Exception as e:
        print(f"❌ Basic fetch failed: {e}")
        return False
    
    return True

def test_caching():
    """Test that caching works."""
    print("\n🧪 Testing caching...")
    
    try:
        fetcher = DataFetcher(cache_hours=1)
        
        # First fetch (should hit API)
        print("   First fetch (from API)...")
        data1 = fetcher.get_stock_data("TSLA", "6mo")
        
        # Second fetch (should use cache)
        print("   Second fetch (from cache)...")
        data2 = fetcher.get_stock_data("TSLA", "6mo")
        
        # Should be identical
        if data1.equals(data2):
            print("✅ Cache working correctly")
        else:
            print("⚠️  Cache data differs from API data")
        
    except Exception as e:
        print(f"❌ Caching test failed: {e}")
        return False
    
    return True

def test_multiple_stocks():
    """Test fetching multiple stocks."""
    print("\n🧪 Testing multiple stocks...")
    
    try:
        fetcher = DataFetcher()
        symbols = ["AAPL", "GOOGL", "MSFT", "INVALID_SYMBOL"]
        
        results = fetcher.get_multiple_stocks(symbols, "1mo")
        
        print(f"✅ Fetched data for {len(results)} out of {len(symbols)} symbols")
        for symbol, data in results.items():
            print(f"   {symbol}: {len(data)} days, latest close: ${data['Close'][-1]:.2f}")
        
    except Exception as e:
        print(f"❌ Multiple stocks test failed: {e}")
        return False
    
    return True

def main():
    """Main test runner function that returns results."""
    print("📊 STONKS Data Super High Tech Fancy Test Suite 🚀\n")
    
    tests = [
        test_basic_fetch,
        test_caching, 
        test_multiple_stocks
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📈 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Ready to build strategies!")
    else:
        print("🔧 Some tests failed. Check your setup.")
    
    return passed, len(tests)


if __name__ == "__main__":
    main()