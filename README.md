# Stonks Dashboard 📈

A Python-based stock analysis dashboard for testing trading strategies against the market.

## Project Structure
```
stonks/
├── README.md
├── requirements.txt
├── data/
│   └── (stock data cache)
├── strategies/
│   ├── __init__.py
│   ├── base_strategy.py
│   └── moving_average.py
├── utils/
│   ├── __init__.py
│   └── data_fetcher.py
├── notebooks/
│   └── exploration.ipynb
├── main.py
└── dashboard.py
```

## Setup

### 1. Clone and Setup Environment
```bash
# Clone your repo
git clone <your-repo-url>
cd stonks-dashboard

# Create conda environment
conda create -n stonks python=3.9
conda activate stonks

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize Git (if starting fresh)
```bash
git init
git add .
git commit -m "Initial project setup"
git remote add origin <your-repo-url>
git push -u origin main
```

### 3. Environment Variables (optional)
```bash
# Copy example environment file
cp .env.example .env
# Edit .env with your API keys if needed
```

3. **Run the dashboard:**
   ```bash
   streamlit run dashboard.py
   ```

## Features

### Current Strategies
- [x] Simple Moving Average Crossover (50/200 day)
- [ ] RSI Mean Reversion
- [ ] MACD Signal
- [ ] Bollinger Bands

### Implemented Features
- [x] Stock data fetching via Yahoo Finance
- [x] Basic backtesting framework
- [ ] Performance metrics vs S&P 500
- [ ] Interactive dashboard
- [ ] Strategy comparison tools

## Usage

### Basic Strategy Test
```python
from strategies.moving_average import MovingAverageStrategy
from utils.data_fetcher import get_stock_data

# Get data
data = get_stock_data("AAPL", period="2y")

# Run strategy
strategy = MovingAverageStrategy(short_window=50, long_window=200)
results = strategy.backtest(data)

print(f"Strategy Return: {results['total_return']:.2%}")
print(f"Buy & Hold Return: {results['buy_hold_return']:.2%}")
```

## Development Log

### 2025-09-13
- Initial project setup
- Created virtual environment "stonks"
- Established project structure and documentation
- Did not go insane
- Also did not sleep a lot

---

**Disclaimer:** This is for my delulu ass to feel better about living in this corporate hellscape we cannot escape. Past performance doesn't guarantee future results. Don't risk money you can't afford to lose! Or do.. but don't make it my problem. 🚀 Love you lots! Go stonk yourself! 