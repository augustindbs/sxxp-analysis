import random
import pandas as pd
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 200)


sxxp = pd.ExcelFile('data/SXXP_daily_10Y.xlsx')
securities_data = {}
securities = sxxp.sheet_names

for security in securities:
    path = f"./data/pkl/{security}.pkl"
    securities_data[security] = pd.read_pickle(path)

for security, df in securities_data.items():
    indicator_rsi = RSIIndicator(df['Close'], window = 21, fillna = True)
    df['RSI'] = indicator_rsi.rsi()
    securities_data[security] = df

    rsi_window = 14
    df[f'RSI SMA{rsi_window}'] = df['RSI'].rolling(rsi_window).mean()
    securities_data[security] = df

    sma_window_short = 21
    indicator_sma = SMAIndicator(df['Close'], window = sma_window_short, fillna = True)
    df[f'SMA{sma_window_short}'] = indicator_sma.sma_indicator()

    sma_window_long = 50
    indicator_sma = SMAIndicator(df['Close'], window = sma_window_long, fillna = True)
    df[f'SMA{sma_window_long}'] = indicator_sma.sma_indicator()


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


def detect_bullish_divergence(price_extrema, rsi_extrema, window_days, lower_barrier):
    
    bullish_divergences = []

    for i in range(len(price_extrema) - 1):
        price_time_1, price_low_1 = price_extrema[i]
        
        if price_low_1 < lower_barrier:  
            for j in range(i + 1, len(price_extrema)):
                price_time_2, price_low_2 = price_extrema[j]

                if (price_time_2 - price_time_1).days <= window_days:
                    rsi_low_1 = next((rsi_val for rsi_time, rsi_val in rsi_extrema if rsi_time == price_time_1), None)
                    rsi_low_2 = next((rsi_val for rsi_time, rsi_val in rsi_extrema if rsi_time == price_time_2), None)

                    if rsi_low_1 is not None and rsi_low_2 is not None:
                        
                        if rsi_low_1 < 30 and price_low_1 > price_low_2 and rsi_low_1 < rsi_low_2:
                            bullish_divergences.append(((price_time_1, price_low_1), (price_time_2, price_low_2)))
                       
                        break
 
    return bullish_divergences


def detect_bearish_divergence(price_extrema, rsi_extrema, window_days, upper_barrier):
    
    bearish_divergences = []

    for i in range(len(price_extrema) - 1):
        price_time_1, price_high_1 = price_extrema[i]

        if price_high_1 > upper_barrier:  
            for j in range(i + 1, len(price_extrema)):
                price_time_2, price_high_2 = price_extrema[j]

                if (price_time_2 - price_time_1).days <= window_days:
                    rsi_high_1 = next((rsi_val for rsi_time, rsi_val in rsi_extrema if rsi_time == price_time_1), None)
                    rsi_high_2 = next((rsi_val for rsi_time, rsi_val in rsi_extrema if rsi_time == price_time_2), None)

                    if rsi_high_1 is not None and rsi_high_2 is not None:
                       
                        if rsi_high_1 > 70 and price_high_1 < price_high_2 and rsi_high_1 > rsi_high_2:
                            bearish_divergences.append(((price_time_1, price_high_1), (price_time_2, price_high_2)))
                       
                        break

    return bearish_divergences

bullish_divergence_securities = []
bearish_divergence_securities = []

t = 60

for security in securities:
    data = securities_data[security][-t:]

    extrema_window = 1
    divergence_window = 30
    upper_barrier = 70
    lower_barrier = 30

    maxima, minima = rw_extrema(data['Close'], extrema_window)
    rsi_maxima, rsi_minima = rw_extrema(data['RSI'], extrema_window)

    bullish_divergences = detect_bullish_divergence(minima, rsi_minima, divergence_window, lower_barrier)
    bearish_divergences = detect_bearish_divergence(maxima, rsi_maxima, divergence_window, upper_barrier)

    if bullish_divergences:
        bullish_divergence_securities.append(security)

    if bearish_divergences:
        bearish_divergence_securities.append(security)


print(f"Bullish divergences in the last {t} days:", bullish_divergence_securities)
print(f"Bearish divergences in the last {t} days:", bearish_divergence_securities)


# PLOTTING


if bullish_divergence_securities or bearish_divergence_securities:

    if bullish_divergence_securities:
        security = random.choice(bullish_divergence_securities)

    else:
        security = random.choice(bearish_divergence_securities)
        
    data = securities_data[security][-t:]

    maxima, minima = rw_extrema(data['Close'], extrema_window)
    rsi_maxima, rsi_minima = rw_extrema(data['RSI'], extrema_window)

    bullish_divergences = detect_bullish_divergence(minima, rsi_minima, divergence_window, lower_barrier)
    bearish_divergences = detect_bearish_divergence(maxima, rsi_maxima, divergence_window, upper_barrier)

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
    ax1.plot(data.index, data[f'SMA{sma_window_short}'], label = f'{sma_window_short}-Day SMA', color = 'blue', alpha = 0.7, linewidth = 0.75)
    ax1.plot(data.index, data[f'SMA{sma_window_long}'], label = f'{sma_window_long}-Day SMA', color = 'magenta', alpha = 0.7, linewidth = 0.75)
    ax1.set_ylabel('Close Price')
    ax1.set_title(f'{security} Extrema and Divergence Detection (Daily)', pad = 30)
    ax1.grid(True, color='gray', alpha = 0.2)
    ax1.legend()

    for maximum in maxima:
        ax1.scatter(maximum[0], maximum[1], marker = 'o', color = 'green', alpha = 0.8, s = 10)
    for minimum in minima:
        ax1.scatter(minimum[0], minimum[1], marker = 'o', color='red', alpha = 0.8, s = 10)

    for (start, end) in bullish_divergences:
        ax1.plot([start[0], end[0]], [start[1], end[1]], color='blue')
    for (start, end) in bearish_divergences:
        ax1.plot([start[0], end[0]], [start[1], end[1]], color='blue')

    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.plot(data.index, data['RSI'], label='Relative Strength Index (RSI)', color = 'orangered', alpha = 0.9, linewidth = 0.75)
    ax2.plot(data.index, data[f'RSI SMA{rsi_window}'], label=f'{rsi_window}-Day RSI SMA', color = 'dodgerblue', alpha = 0.9, linewidth = 0.75)
    ax2.axhline(y=upper_barrier, color = 'red', linestyle = '--', alpha = 0.3)
    ax2.axhline(y=lower_barrier, color = 'red', linestyle = '--', alpha = 0.3)
    ax2.axhline(y=50, color = 'magenta', linestyle = '--', alpha = 0.3)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Relative Strength Index (RSI)')
    ax2.set_ylim(0, 100)
    ax2.grid(True, color='gray', alpha=0.2)
    ax2.legend()

    for rsi_maximum in rsi_maxima:
        ax2.scatter(rsi_maximum[0], rsi_maximum[1], marker = 'o', color='green', alpha = 0.8, s = 5)
    for rsi_minimum in rsi_minima:
        ax2.scatter(rsi_minimum[0], rsi_minimum[1], marker = 'o', color = 'red', alpha = 0.8, s = 5)

    for (start, end) in bullish_divergences:
        ax2.plot([start[0], end[0]], [data.loc[start[0], 'RSI'], data.loc[end[0], 'RSI']], color = 'blue', linewidth = 2)
    for (start, end) in bearish_divergences:
        ax2.plot([start[0], end[0]], [data.loc[start[0], 'RSI'], data.loc[end[0], 'RSI']], color = 'blue', linewidth = 2)

    plt.tight_layout()
    plt.show()

else:
    print("No divergences detected.")
