
import random
import pandas as pd
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator

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

for security, df in securities_data.items():
    indicator_rsi = RSIIndicator(df['Close'], window = 21, fillna = True)
    df['RSI'] = indicator_rsi.rsi()
    securities_data[security] = df


def rw_maximum(data: pd.DataFrame, index: int, window: int) -> bool:
    
    if index < window * 2 + 1 or index >= len(data) - window:
        return False

    maximum = True
    v = data.iloc[index]
    for i in range(1, window + 1):
        if data.iloc[index + i] >= v or data.iloc[index - i] >= v:
            maximum = False
            break

    return maximum


def rw_minimum(data: pd.DataFrame, index: int, window: int) -> bool:
    
    if index < window * 2 + 1 or index >= len(data) - window:
        return False

    minimum = True
    v = data.iloc[index]
    for i in range(1, window + 1):
        if data.iloc[index + i] <= v or data.iloc[index - i] <= v:
            minimum = False
            break

    return minimum

def rw_extrema(data: pd.DataFrame, window: int):
    
    maxima = []
    minima = []

    for i in range(window, len(data) - window):
        if rw_maximum(data, i, window):
            maximum = [data.index[i], data.iloc[i]]
            maxima.append(maximum)

        if rw_minimum(data, i, window):
            minimum = [data.index[i], data.iloc[i]]
            minima.append(minimum)

    return maxima, minima


#--------------------------------------------------------------------------------------------------------------------------------------------------


security = random.choice(securities)
data = securities_data[security][-252:]

window = 2
upper_barrier = 70
lower_barrier = 30

maxima, minima = rw_extrema(data['Close'], window)
rsi_maxima, rsi_minima = rw_extrema(data['RSI'], window)


#--------------------------------------------------------------------------------------------------------------------------------------------------


# PLOTTING


plt.rcParams.update({
    'axes.titlesize': 16,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10
})

fig = plt.figure(figsize = (12, 12))
gs = fig.add_gridspec(2, 1, height_ratios = [4, 3])

ax1 = fig.add_subplot(gs[0])
ax1.plot(data.index, data['Close'], label = 'Close Price', color = 'black', alpha = 0.9, linewidth = 0.75)
ax1.set_ylabel('Close Price')
ax1.set_title(f'{security} Extrema Detection)', pad = 30)
ax1.grid(True, color = 'gray', alpha = 0.2)
ax1.legend()

for maximum in maxima:
    ax1.scatter(maximum[0], maximum[1], marker = 'o', color = 'green', alpha = 0.8, s = 20)
for minimum in minima:
    ax1.scatter(minimum[0], minimum[1], marker = 'o', color = 'red', alpha = 0.8, s = 20)

ax2 = fig.add_subplot(gs[1], sharex = ax1)
ax2.plot(data.index, data['RSI'], label = 'Relative Strength Index (RSI)', color = 'orangered', alpha = 0.9, linewidth = 0.75)
ax2.axhline(y = upper_barrier, color = 'red', linestyle = '--', alpha = 0.3)
ax2.axhline(y = lower_barrier, color = 'red', linestyle = '--', alpha = 0.3)
ax2.axhline(y = 50, color = 'magenta', linestyle = '--', alpha = 0.3)
ax2.set_xlabel('Date')
ax2.set_ylabel('Relative Strength Index (RSI)')
ax2.set_ylim(0, 100)
ax2.grid(True, color = 'gray', alpha = 0.2)
ax2.legend()

for rsi_maximum in rsi_maxima:
    ax2.scatter(rsi_maximum[0], rsi_maximum[1], marker = 'o', color = 'green', alpha = 0.8, s = 20)
for rsi_minimum in rsi_minima:
    ax2.scatter(rsi_minimum[0], rsi_minimum[1], marker = 'o', color = 'red', alpha = 0.8, s = 20)

plt.tight_layout()
plt.show()
