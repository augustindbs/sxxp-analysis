
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import argrelextrema
from collections import defaultdict

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 200)


sxxp = pd.ExcelFile('main/data/SXXP_daily_10Y.xlsx')
securities_data = {}
securities = sxxp.sheet_names

for security in securities:
    path = f"main/data/pkl/{security}.pkl"
    securities_data[security] = pd.read_pickle(path)


def get_max_min(prices, smoothing, window_range):

    smooth_prices = prices['Close'].rolling(window = smoothing).mean().dropna()
    local_max = argrelextrema(smooth_prices.values, np.greater)[0]
    local_min = argrelextrema(smooth_prices.values, np.less)[0]
    
    price_local_max_dt = []
    for i in local_max:
        if (i > window_range) and (i < len(prices) - window_range):
            price_local_max_dt.append(prices.iloc[i - window_range: i + window_range]['Close'].idxmax())
    
    price_local_min_dt = []
    for i in local_min:
        if (i > window_range) and (i < len(prices) - window_range):
            price_local_min_dt.append(prices.iloc[i - window_range: i + window_range]['Close'].idxmin())
    
    maxima = pd.DataFrame(prices.loc[price_local_max_dt])
    minima = pd.DataFrame(prices.loc[price_local_min_dt])
    
    max_min = pd.concat([maxima, minima]).sort_index()
    max_min.index.name = 'Date'
    max_min = max_min.reset_index()
    max_min = max_min[~max_min.Date.duplicated()]
    
    return max_min


n = 30 # Pattern must play out in less than n units

def find_patterns(max_min):
    patterns = defaultdict(list)
    
    for i in range(n, len(max_min)):
        window = max_min.iloc[i-5:i]
        
        if window.index[-1] - window.index[0] > n:
            continue
        
        a, b, c, d, e = window['Close'].iloc[0:5]
        
        # IHS (Inverse Head and Shoulders) pattern detection
        if a < b and c < a and c < e and c < d and e < d and abs(b - d) <= np.mean([b, d]) * 0.01:
            patterns['IHS'].append((window['Date'].iloc[0], window['Date'].iloc[-1]))
    
    return patterns

smoothing = 5
window = 50

security = 'SAF FP Equity'
df = securities_data[security]

minmax = get_max_min(df, smoothing, window)
patterns = find_patterns(minmax)


# PLOTTING


plt.figure(figsize = (14, 12))
plt.plot(df.index, df['Close'], label = 'Close Price', zorder = 1)
plt.scatter(minmax['Date'], minmax['Close'], color = 'red', alpha = 0.5, zorder = 2)
plt.grid(True)
plt.xlabel("Date")
plt.ylabel("Close Price")
plt.legend()

for pattern in patterns['IHS']:
    plt.axvspan(pattern[0], pattern[1], color = 'green', alpha = 0.2, linewidth = 0, label = 'IHS Pattern', zorder = 0)

plt.show()