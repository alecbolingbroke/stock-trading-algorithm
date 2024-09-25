# Stock Trading Algorithm

This project is a stock trading algorithm that implements several strategies (Simple Moving Average, Mean Reversion, and Bollinger Bands) to analyze stock data. The algorithm fetches historical stock data using Yahoo Finance (`yfinance`), evaluates the performance of various strategies, and can execute trades via the Alpaca API. The data and results are saved to CSV and JSON files for analysis.

## Features
- Fetch historical stock data for selected stocks using `yfinance`.
- Implement and evaluate three trading strategies:
  - **Simple Moving Average (SMA)**
  - **Mean Reversion (MR)**
  - **Bollinger Bands (BB)**
- Automatically execute trades based on the best-performing strategy using the Alpaca Paper Trading API.
- Store results in JSON format and the fetched data in CSV files.

## Prerequisites
Before using this script, you need to have the following:
- **Python 3.7+**
- **An Alpaca API account** (for paper trading). You can sign up [here](https://alpaca.markets/).
  
Make sure you have `pip` installed to manage Python packages.

## Installation

### 1. Clone the Repository
First, clone the repository to your local machine:
```bash
git clone https://github.com/alecbolingbroke/stock-trading-algorithm.git
cd stock-trading-algorithm

### 2. Create a Virtual Environment (optional)
For Windows
```bash
python -m venv venv
venv\Scripts\activate

For Mac/Linux
```bash
python3 -m venv venv
source venv/bin/activate

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Setup Environment Variables
Create a .env file to store your API keys, stocks, and desired timeframe of stocks fetched.

ALPACA_API_KEY=your_alpaca_api_key
ALPACA_SECRET_KEY=your_alpaca_secret_key
TIMEFRAME=30
STOCKS=AAPL,MSFT,AMZN,GOOGL,TSLA

### 5. Run the Script
python trading.py

### 6. View Results
After the script runs, you’ll find:

Stock data in CSV files: Located in the data/ folder.
Strategy results in JSON format: Located in the results.json file, which includes the performance of each strategy for each stock and the most profitable strategy.

### Notes
This script uses paper trading by default via the Alpaca API. Paper trading is a simulated environment for testing strategies without real money.
Ensure that the .env file is never shared publicly, as it contains sensitive information such as API keys.

### Trouble-shooting
1. Missing Dependencies: If the script fails due to missing dependencies, ensure you’ve installed them using the pip install -r requirements.txt command.
2. Incorrect API Keys: If you receive errors regarding authentication, double-check your Alpaca API keys in the .env file.
3. Connection Issues: Make sure your network allows access to the Alpaca API and that your API keys are valid.

### Disclaimer
This project is for educational purposes only. The author is not responsible for any financial losses or damages resulting from the use of this script. Always backtest your strategies thoroughly before using them in a live trading environment.


