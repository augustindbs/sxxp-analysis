
import pandas as pd
import matplotlib.pyplot as plt

from ta.trend import MACD, SMAIndicator, EMAIndicator, ADXIndicator
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 200)

sxxp = pd.ExcelFile('data/SXXP_daily_10Y.xlsx') 
securities_data = {}
security_names = sxxp.sheet_names

for security in security_names:
    path = f"pkl/{security}.pkl"
    securities_data[security] = pd.read_pickle(path)

# Simply moving averages
for security, df in securities_data.items():
    indicator_sma141 = SMAIndicator(df['Close'], window = 14, fillna = True)
    df['SMA14'] = indicator_sma141.sma_indicator()
    securities_data[security] = df

# Exponential moving averages
for security, df in securities_data.items():
    indicator_ema_short = EMAIndicator(df['Close'], window = 5, fillna = True)
    indicator_ema_long = EMAIndicator(df['Close'], window = 20, fillna = True)
    df['EMA5'] = indicator_ema_short.ema_indicator()
    df['EMA20'] = indicator_ema_long.ema_indicator()
    df['EMA Crossover'] = indicator_ema_short.ema_indicator() - indicator_ema_long.ema_indicator()
    securities_data[security] = df

# MACD difference indicator
for security, df in securities_data.items():
    indicator_macd = MACD(df['Close'], window_slow = 26, window_fast = 12, window_sign = 9, fillna = True)
    df['MACD_diff'] = indicator_macd.macd_diff()
    securities_data[security] = df

# Bollinger bands 
for security, df in securities_data.items():
    bollinger_bands = BollingerBands(df['Close'], window = 20, window_dev = 2, fillna = True)
    df['BB_low'] = bollinger_bands.bollinger_lband()
    df['BB_mavg'] = bollinger_bands.bollinger_mavg()
    df['BB_high'] = bollinger_bands.bollinger_hband()
    securities_data[security] = df

# RSI indicator
for security, df in securities_data.items():
    indicator_rsi = RSIIndicator(df['Close'], window = 14, fillna = True)
    df['RSI'] = indicator_rsi.rsi()
    securities_data[security] = df

# ADX indicator
for security, df in securities_data.items():
    indicator_adx = ADXIndicator(df['High'], df['Low'], df['Close'], window = 14, fillna = True)
    df['ADX'] = indicator_adx.adx()
    securities_data[security] = df

print(securities_data['SAF FP Equity'].head(200)) # Example on Safran stock, last 200 days


# PLOTTING EXAMPLE


plt.figure(figsize = (14, 12))
dates = securities_data['SAF FP Equity'].index
macd_diff = securities_data['SAF FP Equity']['MACD_diff']

bars = plt.bar(dates, macd_diff, color = ['red' if x < 0 else 'green' for x in macd_diff])

plt.grid(True)
plt.title("SAF FP Equity MACD Difference")
plt.xlabel("Date")
plt.ylabel("MACD Difference")
plt.xticks(rotation = 45)
plt.tight_layout()

plt.show()









