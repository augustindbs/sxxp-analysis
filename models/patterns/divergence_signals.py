
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random

from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

import yfinance as yf

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 200)


# LOADING DATA (FREQUENCY = DAILY IN THE ORIGINAL DATASET)


sxxp = pd.ExcelFile('main/data/sxxp_daily.xlsx')
securities_data = {}
securities = sxxp.sheet_names

for security in securities:
    path = f"./main/data/pkl/{security}.pkl"
    securities_data[security] = pd.read_pickle(path)

for security, df in securities_data.items():
    indicator_rsi = RSIIndicator(df['Close'], window = 21, fillna = True)
    df['RSI'] = indicator_rsi.rsi()
    
    rsi_window = 14
    df[f'RSI SMA{rsi_window}'] = df['RSI'].rolling(rsi_window).mean()
    securities_data[security] = df
    
    sma_window_short = 21
    indicator_sma = SMAIndicator(df['Close'], window = sma_window_short, fillna = True)
    df[f'SMA{sma_window_short}'] = indicator_sma.sma_indicator()

    sma_window_long = 50
    indicator_sma = SMAIndicator(df['Close'], window = sma_window_long, fillna = True)
    df[f'SMA{sma_window_long}'] = indicator_sma.sma_indicator()

start_date = '2014-01-10'

securities_weekly_data = {}

for security, df in securities_data.items():
    weekly_df = df.resample('W-FRI', closed = 'right', label = 'right').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum',
        'RSI': 'last',
        f'RSI SMA{rsi_window}': 'last',
        f'SMA{sma_window_short}': 'last',
        f'SMA{sma_window_long}': 'last'
    })

    weekly_df.dropna(inplace = True)

    weekly_df = weekly_df[start_date:]

    securities_weekly_data[security] = weekly_df


def divergence(df: pd.DataFrame, indicator: str, lower_barrier: float, upper_barrier: float, window: int, buy_col: str, sell_col: str):
    
    df = df.copy()
    df[buy_col] = np.nan
    df[sell_col] = np.nan

    # Bullish divergence
    for i in range(len(df)):
        if df.iloc[i][indicator] < lower_barrier:
            for a in range(i + 1, min(i + window, len(df))):
                if 50 > df.iloc[a][indicator] > lower_barrier:
                    for r in range(a + 1, min(a + window, len(df))):
                        if df.iloc[r][indicator] < (lower_barrier + (lower_barrier/10)) and df.iloc[r][indicator] > df.iloc[i][indicator] and df.iloc[r]['Close'] < df.iloc[i]['Close']:
                            for s in range(r + 1, min(r + window, len(df))):
                                if df.iloc[s][indicator] > df.iloc[r][indicator]:
                                    df.at[df.index[s + 1], buy_col] = 1
                                    break
                            break
                        elif df.iloc[r][indicator] > 50:
                            break
                    break
                elif df.iloc[a][indicator] > 50:
                    break
    
    # Bearish divergence
    for i in range(len(df)):
        if df.iloc[i][indicator] > upper_barrier:
            for a in range(i + 1, min(i + window, len(df))):
                if 50 < df.iloc[a][indicator] < upper_barrier:
                    for r in range(a + 1, min(a + window, len(df))):
                        if df.iloc[r][indicator] > (upper_barrier - (upper_barrier/10)) and df.iloc[r][indicator] < df.iloc[i][indicator] and df.iloc[r]['Close'] > df.iloc[i]['Close']:
                            for s in range(r + 1, min(r + window, len(df))):
                                if df.iloc[s][indicator] < df.iloc[r][indicator]:
                                    df.at[df.index[s + 1], sell_col] = -1
                                    break
                            break
                        elif df.iloc[r][indicator] < 50:
                            break
                    break
                elif df.iloc[a][indicator] < 50:
                    break

    return df


#--------------------------------------------------------------------------------------------------------------------------------------------------


security = random.choice(securities)
frequency = 'Daily'
t = 100


if frequency == 'Daily':
    data = securities_data[security][-t:]
elif frequency == 'Weekly':
    data = securities_weekly_data[security][-t:]

data_frequency = 'Daily'
if data.index.freq is not None and 'W-' in data.index.freqstr:
    data_frequency = 'Weekly'


lower_barrier = 30
upper_barrier = 70
window = 30


data_with_signals = divergence(data, 'RSI', lower_barrier, upper_barrier, window, 'Buy Signal', 'Sell Signal') 


#--------------------------------------------------------------------------------------------------------------------------------------------------


def calculate_pnl(data: pd.DataFrame, initial_capital: float, trade_amount: float):
    
    capital = initial_capital
    position = 0
    pnl = []

    for i in range(len(data)):
        if data.iloc[i]['Buy Signal'] == 1:
            if capital >= trade_amount:
                position += trade_amount / data.iloc[i]['Close']
                capital -= trade_amount

        elif data.iloc[i]['Sell Signal'] == -1:
            if position > 0:
                sell_value = position * data.iloc[i]['Close']
                capital += sell_value
                position = 0

        portfolio_value = capital + position * data.iloc[i]['Close']
        pnl.append(portfolio_value)

    data['PnL'] = pnl
    return data


initial_capital = 100000
trade_amount = 100000
data_with_pnl = calculate_pnl(data_with_signals, initial_capital, trade_amount)


if data_with_pnl['PnL'].mean() == 100000:
    print('----------------------------------------------------------------------------------------------------------------------')
    print(f'No position was taken for {security}')
    print('----------------------------------------------------------------------------------------------------------------------')

else:
    print(data_with_pnl)
    print('----------------------------------------------------------------------------------------------------------------------')
    total_profit = (data_with_pnl['PnL'].iloc[-1] - initial_capital) / initial_capital
    print(f'Total profit = {total_profit:.2%}')
    print('----------------------------------------------------------------------------------------------------------------------')


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

if frequency == 'Daily':
    ax1.plot(data.index, data[f'SMA{sma_window_short}'], label = f'{sma_window_short}-Day SMA', color = 'blue', alpha = 0.7, linewidth = 0.75)
    ax1.plot(data.index, data[f'SMA{sma_window_long}'], label = f'{sma_window_long}-Day SMA', color = 'magenta', alpha = 0.7, linewidth = 0.75)

buy_signals = data_with_signals[data_with_signals['Buy Signal'] == 1]
sell_signals = data_with_signals[data_with_signals['Sell Signal'] == -1]
ax1.scatter(buy_signals.index, buy_signals['Close'], marker = 'o', color = 'green', s = 50, label = 'Buy Signal')
ax1.scatter(sell_signals.index, sell_signals['Close'], marker = 'o', color = 'red', s = 50, label = 'Sell Signal')
ax1.set_ylabel('Close Price')
ax1.set_title(f'{security} Divergences Detection ({data_frequency})', pad = 30)
ax1.grid(True, color = 'gray', alpha = 0.2)
ax1.legend()

ax2 = fig.add_subplot(gs[1], sharex = ax1)
ax2.plot(data.index, data['RSI'], label = 'Relative Strength Index (RSI)', color = 'orangered', alpha = 0.9, linewidth = 0.75)
ax2.plot(data.index, data[f'RSI SMA{rsi_window}'], label = f'{rsi_window}-Day RSI SMA', color = 'dodgerblue', alpha = 0.9, linewidth = 0.75)
ax2.axhline(y = upper_barrier, color = 'red', linestyle = '--', alpha = 0.5, linewidth = 0.75)
ax2.axhline(y = lower_barrier, color = 'red', linestyle = '--', alpha = 0.5, linewidth = 0.75)
ax2.axhline(y = 50, color = 'magenta', linestyle = '--', alpha = 0.5, linewidth = 0.75)

ax2.scatter(buy_signals.index, buy_signals['RSI'], marker = 'o', color = 'green', alpha = 0.8, s = 30)
ax2.scatter(sell_signals.index, sell_signals['RSI'], marker = 'o', color = 'red', alpha = 0.8, s = 30)
ax2.set_xlabel('Date')
ax2.set_ylabel('Relative Strength Index (RSI)')
ax2.set_ylim(0, 100)
ax2.grid(True, color = 'gray', alpha = 0.2)
ax2.legend()

plt.tight_layout()
plt.show()
