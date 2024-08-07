
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

from ta.trend import SMAIndicator

from data.sxxp_securities import sxxp_tickers

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 200)

securities_data = {}

for ticker in sxxp_tickers:
    try:
        data = yf.download(ticker, period = 'max', interval = '1d')
        
        if not data.empty:
            securities_data[ticker] = data
    
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")

for ticker, df in securities_data.items():
    indicator_sma = SMAIndicator(df['Adj Close'], window = 141, fillna = False)
    df['SMA141'] = indicator_sma.sma_indicator()
    securities_data[ticker] = df

def ma_crossover(securities_data):
    crossover_securities = []

    for ticker, df in securities_data.items():
        df['Prev_Adj_Close'] = df['Adj Close'].shift(1)
        df['Prev_SMA141'] = df['SMA141'].shift(1)

        df['Crossover'] = ((df['Prev_Adj_Close'] < df['Prev_SMA141']) & (df['Adj Close'] > df['SMA141'])).astype(int) - \
                          ((df['Prev_Adj_Close'] > df['Prev_SMA141']) & (df['Adj Close'] < df['SMA141'])).astype(int)

        if df['Crossover'].iloc[-1] != 0:
            crossover_type = 'over' if df['Crossover'].iloc[-1] == 1 else 'under'
            crossover_securities.append((ticker, crossover_type))

    return crossover_securities

crossover_securities = ma_crossover(securities_data)

for ticker, crossover_type in crossover_securities:
    print(f"{ticker} crossover: {crossover_type}")

def plot_security(ticker, df):
    plt.figure(figsize = (14, 7))
    plt.plot(df.index, df['Adj Close'], label = 'Adjusted Close Price')
    plt.plot(df.index, df['SMA141'], label = 'SMA141', alpha = 0.7)
    plt.title(f"{ticker} Price and SMA141")
    plt.legend()
    plt.show()

for security, data in crossover_securities:
    plot_security(security, securities_data[security])