
import pandas as pd
import numpy as np

from ta.momentum import RSIIndicator

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


def divergence(df: pd.DataFrame, indicator: str, lower_barrier: float, upper_barrier: float, window: int, buy_col: str, sell_col: str):
    
    df = df.copy()
    df[buy_col] = np.nan
    df[sell_col] = np.nan

    # Bullish divergence
    for i in range(len(df) - 1):
        if df.iloc[i][indicator] < lower_barrier:
            for a in range(i + 1, min(i + window, len(df))):
                if 50 > df.iloc[a][indicator] > lower_barrier:
                    for r in range(a + 1, min(a + window, len(df))):
                        if df.iloc[r][indicator] < (lower_barrier + (lower_barrier/10)) and df.iloc[r][indicator] > df.iloc[i][indicator] and df.iloc[r]['Close'] < df.iloc[i]['Close']:
                            for s in range(r + 1, min(r + window, len(df) - 1)):
                                if df.iloc[s][indicator] > df.iloc[r][indicator]:
                                    df.loc[df.index[s + 1], buy_col] = 1
                                    break
                            break
                        elif df.iloc[r][indicator] > 50:
                            break
                    break
                elif df.iloc[a][indicator] > 50:
                    break
    
    # Bearish divergence
    for i in range(len(df) - 1):
        if df.iloc[i][indicator] > upper_barrier:
            for a in range(i + 1, min(i + window, len(df))):
                if 50 < df.iloc[a][indicator] < upper_barrier:
                    for r in range(a + 1, min(a + window, len(df))):
                        if df.iloc[r][indicator] > (upper_barrier - (upper_barrier/10)) and df.iloc[r][indicator] < df.iloc[i][indicator] and df.iloc[r]['Close'] > df.iloc[i]['Close']:
                            for s in range(r + 1, min(r + window, len(df) - 1)):
                                if df.iloc[s][indicator] < df.iloc[r][indicator]:
                                    df.loc[df.index[s + 1], sell_col] = -1
                                    break
                            break
                        elif df.iloc[r][indicator] < 50:
                            break
                    break
                elif df.iloc[a][indicator] < 50:
                    break

    return df


#--------------------------------------------------------------------------------------------------------------------------------------------------


t = 252
lower_barrier = 30
upper_barrier = 70
window = 10

initial_capital = 100000
trade_amount = 50000


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

pnl = {}
total_positions = 0
profitable_trades = 0
losing_trades = 0
total_pnl = 0

for security, df in securities_data.items():
    indicator_rsi = RSIIndicator(df['Close'], window = 21, fillna = True)
    df['RSI'] = indicator_rsi.rsi()

    rsi_window = 14
    df[f'RSI SMA{rsi_window}'] = df['RSI'].rolling(rsi_window).mean()

    data_with_signals = divergence(df[-t:], 'RSI', lower_barrier, upper_barrier, window, 'Buy Signal', 'Sell Signal')
    data_with_pnl = calculate_pnl(data_with_signals, initial_capital, trade_amount)

    if not data_with_pnl.empty and data_with_pnl['PnL'].mean() != 100000:
        pnl[security] = data_with_pnl['PnL'].iloc[-1]
        total_positions += 1
        total_pnl += data_with_pnl['PnL'].iloc[-1]

        if data_with_pnl['PnL'].iloc[-1] > initial_capital:
            profitable_trades += 1
        else:
            losing_trades += 1

if total_positions > 0:
    average_pnl = total_pnl / total_positions
else:
    average_pnl = 0


# PRINTING RESULTS


print('======================================================================================================================')
print(pnl)
print('======================================================================================================================')
print(f"Total positions taken: {total_positions}")
print(f"Number of profitable trades: {profitable_trades}")
print(f"Number of losing trades: {losing_trades}")
print(f"Hit ratio: {profitable_trades / (profitable_trades + losing_trades):.2%}")
print(f"Average PnL across all positions: {average_pnl}")
print('======================================================================================================================')


