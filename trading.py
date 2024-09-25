#! /usr/bin/env python3
import yfinance as yf
import pandas as pd
import numpy as np
import json
import alpaca_trade_api as tradeapi
from pathlib import Path
import os
import datetime
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Get API keys and other settings from environment variables
api_key = os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_SECRET_KEY')
time_variable = int(os.getenv('TIMEFRAME', 30))  # Default to 30 days if not set

# Check if API keys exist
if not api_key or not secret_key:
    raise ValueError("Alpaca API key and secret must be set in the environment variables.")

# Get the current working directory
cwd = Path.cwd()

# Set custom directory within current working directory
data_dir = cwd / 'data'
results_file = cwd / 'results.json'

# Create the directory if it does not exist
data_dir.mkdir(parents=True, exist_ok=True)

# Print where data will be saved
print(f"Data will be saved in {data_dir}")

# List of stocks from environment variable
stocks = os.getenv('STOCKS')

# Convert the comma-separated string to a list
if stocks:
    stocks = stocks.split(',')
else:
    # Default stocks list if the environment variable is not set
    stocks = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA']

# Create Alpaca API client
api = tradeapi.REST(api_key, secret_key, base_url="https://paper-api.alpaca.markets")

# Calculate start and end dates
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=time_variable)

# Fetch data for stocks and save to csv
for stock in stocks:
    data = yf.download(stock, start=start_date, end=end_date)
    data.to_csv(data_dir / f'{stock}.csv')

print(f"Data has been fetched and saved for the last {time_variable} days ({start_date} to {end_date}).")

# Calculate moving (rolling) averages for each stock
def calculate_moving_averages(prices, window=5):
    return prices.rolling(window=window).mean()

# Simple moving average strategy
def simple_moving_average_strategy(data, short_window=5, long_window=20):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    # Short moving average
    signals['short_mavg'] = calculate_moving_averages(data['Close'], window=short_window)
    # Long moving average
    signals['long_mavg'] = calculate_moving_averages(data['Close'], window=long_window)

    # Create signals
    signals.loc[signals.index[short_window:], 'signal'] = np.where(
        signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, -1.0
    )
    signals['positions'] = signals['signal'].diff()

    return signals

# Mean reversion strategy
def mean_reversion_strategy(data, window=20, std_dev_factor=1.0):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Close']
    signals['mean'] = data['Close'].rolling(window=window).mean()
    signals['std'] = data['Close'].rolling(window=window).std()
    signals['signal'] = 0.0

    # Buy signals
    signals['signal'] = np.where(signals['price'] < signals['mean'] - std_dev_factor * signals['std'], 1.0, 0.0)
    # Sell signals
    signals['signal'] = np.where(signals['price'] > signals['mean'] + std_dev_factor * signals['std'], -1.0, signals['signal'])

    return signals

# Bollinger bands strategy
def bollinger_bands_strategy(data, window=20, num_std_dev=2):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Close']

    # Middle Band = 20 day (window) simple moving average
    signals['middle_band'] = data['Close'].rolling(window=window).mean()

    # Standard Deviation
    rolling_std = data['Close'].rolling(window=window).std()

    # Upper band
    signals['upper_band'] = signals['middle_band'] + (num_std_dev * rolling_std)

    # Lower band
    signals['lower_band'] = signals['middle_band'] - (num_std_dev * rolling_std)

    # Create signals
    signals['signal'] = 0.0

    # Buy signals
    signals['signal'] = np.where(signals['price'] < signals['lower_band'], 1.0, 0.0)

    # Sell signals
    signals['signal'] = np.where(signals['price'] > signals['upper_band'], -1.0, signals['signal'])

    return signals

# Calculate profit
def calculate_profit(signals, prices):
    profit = 0
    position_open = False
    entry_price = 0

    for signal, price in zip(signals, prices):
        if signal == 1 and not position_open:
            position_open = True
            entry_price = price
        elif signal == -1 and position_open:
            position_open = False
            profit += price - entry_price

    return profit

# Evaluate strategies
def evaluate_strategies(stocks):
    results = {}
    most_profitable = {
        'Stock': None,
        'Strategy': None,
        'Profit': float('-inf')
    }

    for stock in stocks:
        print(f'Processing {stock}...')
        data = pd.read_csv(data_dir / f"{stock}.csv", index_col="Date", parse_dates=True)

        # Apply strategies
        sma_signals = simple_moving_average_strategy(data)
        mr_signals = mean_reversion_strategy(data)
        bb_signals = bollinger_bands_strategy(data)

        # Calculate profit
        sma_profit = calculate_profit(sma_signals['signal'], data['Close'])
        mr_profit = calculate_profit(mr_signals['signal'], data['Close'])
        bb_profit = calculate_profit(bb_signals['signal'], data['Close'])

        # Update results for each strategy
        strategies = {
            'sma': {
                'buy_signals': int((sma_signals['signal'] > 0).sum()),
                'sell_signals': int((sma_signals['signal'] < 0).sum()),
                'Profit': float(sma_profit)},
            'mr': {
                'buy_signals': int((mr_signals['signal'] > 0).sum()),
                'sell_signals': int((mr_signals['signal'] < 0).sum()),
                'Profit': float(mr_profit)},
            'bb': {
                'buy_signals': int((bb_signals['signal'] > 0).sum()),
                'sell_signals': int((bb_signals['signal'] < 0).sum()),
                'Profit': float(bb_profit)}
        }

        # Determine best strategy for each stock
        best_strategy = max(strategies.items(), key=lambda k: k[1]['Profit'])[0]

        # Store results
        results[stock] = {'strategies': strategies, 'best_strategy': best_strategy}

        for strategy, stats in strategies.items():
            if stats['Profit'] > most_profitable['Profit']:
                most_profitable.update({
                    'Stock': stock,
                    'Strategy': strategy,
                    'Profit': float(stats['Profit'])
                })

    # Save results to JSON file
    with open(results_file, 'w') as f:
        json.dump({'results': results, 'most_profitable': most_profitable}, f)

    return results

results = evaluate_strategies(stocks)

def fetch_and_trade():
    with open(results_file, 'r') as f:
        best_strategies = json.load(f)['results']

        for stock, data in best_strategies.items():
            best_strategy = data['best_strategy']
            latest_data = yf.download(stock, period='1d', interval='1m')  # Fetch most recent data

            # Find which strategy is best for which stock
            if best_strategy == 'sma':
                signals = simple_moving_average_strategy(latest_data)
            elif best_strategy == 'mr':
                signals = mean_reversion_strategy(latest_data)
            elif best_strategy == 'bb':
                signals = bollinger_bands_strategy(latest_data)

            # Get latest signal
            latest_signal = signals['signal'].iloc[-1]

            # Execute order based on latest signal
            if latest_signal > 0:
                api.submit_order(
                    symbol=stock,
                    qty=10,
                    side='buy',
                    type='market',
                    time_in_force='gtc',
                )
                print(f'Executed BUY order for {stock} based on {best_strategy.upper()} strategy')
            elif latest_signal < 0:
                api.submit_order(
                    symbol=stock,
                    qty=10,
                    side='sell',
                    type='market',
                    time_in_force='gtc',
                )
                print(f'Executed SELL order for {stock} based on {best_strategy.upper()} strategy')
            else:
                print(f'Hold signal for {stock} based on {best_strategy.upper()} strategy')

fetch_and_trade()
