
import pandas as pd
import yfinance as yf
import tkinter as tk
import matplotlib.pyplot as plt

from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

from tkinter import ttk

from data.sxxp_securities import sxxp_tickers

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 200)


securities_data = {}

for ticker in sxxp_tickers:
    data = yf.download(ticker, period = '1y', interval = '1d')
    securities_data[ticker] = data

sma_window_short = 14
sma_window_long = 50

for ticker, df in securities_data.items():
    indicator_rsi = RSIIndicator(df['Adj Close'], window = 21, fillna = True)
    df['RSI'] = indicator_rsi.rsi()
    df['RSI SMA14'] = df['RSI'].rolling(14).mean()

    indicator_sma_short = SMAIndicator(df['Adj Close'], window = sma_window_short, fillna = True)
    df[f'SMA{sma_window_short}'] = indicator_sma_short.sma_indicator()

    indicator_sma_long = SMAIndicator(df['Adj Close'], window = sma_window_long, fillna = True)
    df[f'SMA{sma_window_long}'] = indicator_sma_long.sma_indicator()

    df['Volume SMA14'] = df['Volume'].rolling(14).mean()

    securities_data[ticker] = df


def rw_maximum(data, index, window):

    """
    Returns the maximum point in a prespecified window.
    """
    
    if index < window * 2 + 1 or index >= len(data) - window:
        return False

    maximum = True
    v = data.iloc[index]

    for i in range(1, window + 1):
        if data.iloc[index + i] >= v or data.iloc[index - i] >= v:
            maximum = False
            break

    return maximum


def rw_minimum(data, index, window):

    """
    Returns the minimum point in a prespecified window.
    """
    
    if index < window * 2 + 1 or index >= len(data) - window:
        return False

    minimum = True
    v = data.iloc[index]

    for i in range(1, window + 1):
        if data.iloc[index + i] <= v or data.iloc[index - i] <= v:
            minimum = False
            break

    return minimum


def rw_extrema(data, window):

    """
    Returns the list of all maxima and minima within a prespecified window.
    """
    
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


def detect_bullish_divergence(price_extrema, rsi_extrema, window_days, lower_barrier, data):

    """
    Given lists of extrema points found both in adjusted close price and RSI data, detects whether or not a bullish divergence is present within a window of size window_days or less.
    """
    
    bullish_divergences = []

    for i in range(len(price_extrema) - 1):
        price_time_1, price_low_1 = price_extrema[i]

        for j in range(i + 1, len(price_extrema)):
            price_time_2, price_low_2 = price_extrema[j]

            if (price_time_2 - price_time_1).days <= window_days:
                rsi_low_1 = next((rsi_val for rsi_time, rsi_val in rsi_extrema if rsi_time == price_time_1), None)
                rsi_low_2 = next((rsi_val for rsi_time, rsi_val in rsi_extrema if rsi_time == price_time_2), None)

                if rsi_low_1 is not None and rsi_low_2 is not None:
                    
                    if rsi_low_1 < lower_barrier and price_low_1 > price_low_2 and rsi_low_1 < rsi_low_2:
                        valid_divergence = True
                        
                        for date in data.index:
                            if price_time_1 <= date <= price_time_2:
                                price_value = data.loc[date, 'Adj Close']
                                y_divergence = price_low_1 + (price_low_2 - price_low_1) * ((date - price_time_1).days / (price_time_2 - price_time_1).days)
                                
                                if price_value < y_divergence:
                                    valid_divergence = False
                                    break

                        if valid_divergence:
                            span_days = (price_time_2 - price_time_1).days
                            bullish_divergences.append(((price_time_1, price_low_1), (price_time_2, price_low_2), span_days))
                    break

    return bullish_divergences


def detect_bearish_divergence(price_extrema, rsi_extrema, window_days, upper_barrier, data):

    """
    Given lists of extrema points found both in adjusted close price and RSI data, detects whether or not a bearish divergence is present within a window of size window_days or less.
    """
   
    bearish_divergences = []

    for i in range(len(price_extrema) - 1):
        price_time_1, price_high_1 = price_extrema[i]

        for j in range(i + 1, len(price_extrema)):
            price_time_2, price_high_2 = price_extrema[j]

            if (price_time_2 - price_time_1).days <= window_days:
                rsi_high_1 = next((rsi_val for rsi_time, rsi_val in rsi_extrema if rsi_time == price_time_1), None)
                rsi_high_2 = next((rsi_val for rsi_time, rsi_val in rsi_extrema if rsi_time == price_time_2), None)

                if rsi_high_1 is not None and rsi_high_2 is not None:
                    
                    if rsi_high_1 > upper_barrier and price_high_1 < price_high_2 and rsi_high_1 > rsi_high_2:
                        valid_divergence = True
                        
                        for date in data.index:
                            if price_time_1 <= date <= price_time_2:
                                price_value = data.loc[date, 'Adj Close']
                                y_divergence = price_high_1 + (price_high_2 - price_high_1) * ((date - price_time_1).days / (price_time_2 - price_time_1).days)
                                
                                if price_value > y_divergence:
                                    valid_divergence = False
                                    break

                        if valid_divergence:
                            span_days = (price_time_2 - price_time_1).days
                            bearish_divergences.append(((price_time_1, price_high_1), (price_time_2, price_high_2), span_days))
                    break

    return bearish_divergences


def plot_graph(ticker, t, extrema_window, divergence_window, upper_barrier, lower_barrier, sma_window_short, sma_window_long, securities_data):

    """
    Plots adjust close price, RSI and volume graphs for a given security.
    """
    
    data = securities_data[ticker][-t:]

    indicator_sma_short = SMAIndicator(data['Adj Close'], window = sma_window_short, fillna = True)
    data[f'SMA{sma_window_short}'] = indicator_sma_short.sma_indicator()

    indicator_sma_long = SMAIndicator(data['Adj Close'], window = sma_window_long, fillna = True)
    data[f'SMA{sma_window_long}'] = indicator_sma_long.sma_indicator()

    maxima, minima = rw_extrema(data['Adj Close'], extrema_window)
    rsi_maxima, rsi_minima = rw_extrema(data['RSI'], extrema_window)

    bullish_divergences = detect_bullish_divergence(minima, rsi_minima, divergence_window, lower_barrier, data)
    bearish_divergences = detect_bearish_divergence(maxima, rsi_maxima, divergence_window, upper_barrier, data)

    plt.rcParams.update({
        'axes.titlesize': 16,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10
    })

    fig = plt.figure(figsize = (12, 12))
    gs = fig.add_gridspec(3, 1, height_ratios = [4, 3, 1])

    ax1 = fig.add_subplot(gs[0])
    ax1.plot(data.index, data['Adj Close'], label = 'Adjusted Close Price', color = 'black', alpha = 0.9, linewidth = 0.75)
    ax1.plot(data.index, data[f'SMA{sma_window_short}'], label = f'{sma_window_short}-Day SMA', color = 'blue', alpha = 0.7, linewidth = 0.75)
    ax1.plot(data.index, data[f'SMA{sma_window_long}'], label = f'{sma_window_long}-Day SMA', color = 'magenta', alpha = 0.7, linewidth = 0.75)
    ax1.set_ylabel('Adjusted Close Price')
    ax1.set_title(f'{ticker} Extrema and Divergence Detection (Daily)', pad = 30)
    ax1.grid(True, color = 'gray', alpha = 0.2)
    ax1.legend()

    for maximum in maxima:
        ax1.scatter(maximum[0], maximum[1], marker = 'o', color = 'green', alpha = 0.8, s = 10)
    for minimum in minima:
        ax1.scatter(minimum[0], minimum[1], marker = 'o', color = 'red', alpha = 0.8, s = 10)

    for (start, end, span_days) in bullish_divergences:
        ax1.plot([start[0], end[0]], [start[1], end[1]], color = 'blue', linestyle = '--', linewidth = 2)
        ax1.scatter(end[0], end[1] * 0.99, marker = '^', color = 'green', s = 80, zorder = 5)
    for (start, end, span_days) in bearish_divergences:
        ax1.plot([start[0], end[0]], [start[1], end[1]], color = 'blue', linestyle = '--', linewidth = 2)
        ax1.scatter(end[0], end[1] * 1.01, marker = 'v', color = 'red', s = 80, zorder = 5)

    ax2 = fig.add_subplot(gs[1], sharex = ax1)
    ax2.plot(data.index, data['RSI'], label = '21-Day RSI', color = 'orangered', alpha = 0.9, linewidth = 0.75)
    ax2.plot(data.index, data[f'RSI SMA14'], color = 'dodgerblue', alpha = 0.9, linewidth = 0.75)
    ax2.axhline(y = upper_barrier, color = 'red', linestyle = '--', alpha = 0.3)
    ax2.axhline(y = lower_barrier, color = 'red', linestyle = '--', alpha = 0.3)
    ax2.axhline(y = 50, color = 'magenta', linestyle = '--', alpha = 0.3)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Relative Strength Index (RSI)')
    ax2.set_ylim(0, 100)
    ax2.grid(True, color = 'gray', alpha = 0.2)
    ax2.legend()

    for rsi_maximum in rsi_maxima:
        ax2.scatter(rsi_maximum[0], rsi_maximum[1], marker = 'o', color = 'green', alpha = 0.8, s = 5)
    for rsi_minimum in rsi_minima:
        ax2.scatter(rsi_minimum[0], rsi_minimum[1], marker = 'o', color = 'red', alpha = 0.8, s = 5)

    for (start, end, span_days) in bullish_divergences:
        ax2.plot([start[0], end[0]], [data.loc[start[0], 'RSI'], data.loc[end[0], 'RSI']], color = 'blue', linewidth = 2, linestyle = '--')
    for (start, end, span_days) in bearish_divergences:
        ax2.plot([start[0], end[0]], [data.loc[start[0], 'RSI'], data.loc[end[0], 'RSI']], color = 'blue', linewidth = 2, linestyle = '--')

    ax3 = fig.add_subplot(gs[2], sharex = ax1)
    ax3.bar(data.index, data['Volume'], label = 'Volume', color = 'darkgreen', alpha = 0.7)
    ax3.plot(data.index, data['Volume SMA14'], color = 'springgreen')
    ax3.set_ylabel('Volume')
    ax3.set_xlabel('Date')
    ax3.grid(True, color = 'gray', alpha = 0.2)
    ax3.legend()

    plt.tight_layout()
    plt.show()


def detect_divergences(ticker, t, extrema_window, divergence_window, upper_barrier, lower_barrier, securities_data):

    """
    Returns all bullish and bearish divergences detected in a security's data for a lookback period of t days.
    """
    
    data = securities_data[ticker][-t:]

    maxima, minima = rw_extrema(data['Adj Close'], extrema_window)
    rsi_maxima, rsi_minima = rw_extrema(data['RSI'], extrema_window)

    bullish_divergences = detect_bullish_divergence(minima, rsi_minima, divergence_window, lower_barrier, data)
    bearish_divergences = detect_bearish_divergence(maxima, rsi_maxima, divergence_window, upper_barrier, data)

    return bullish_divergences, bearish_divergences


# GUI WINDOW CREATION


def create_gui(securities_data):

    """
    Creates GUI window for given security in the given time period.
    """
   
    def show_divergences():

        """
        Shows divergences found for given security in the given time period.
        """
        
        try:
            upper_barrier_val = int(upper_barrier_entry.get())
            lower_barrier_val = int(lower_barrier_entry.get())
            sma_short_val = int(sma_short_entry.get())
            sma_long_val = int(sma_long_entry.get())
            extrema_window_val = int(extrema_window_entry.get())
            divergence_window_val = int(divergence_window_entry.get())
            t_val = int(t_entry.get())

            divergence_window = tk.Toplevel(root)
            divergence_window.title('Divergences Detected')
            divergence_window.geometry('300x600')

            canvas = tk.Canvas(divergence_window)
            canvas.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)

            scrollbar = tk.Scrollbar(divergence_window, orient = tk.VERTICAL, command = canvas.yview)
            scrollbar.pack(side = tk.RIGHT, fill = tk.Y)

            canvas.configure(yscrollcommand = scrollbar.set, scrollregion = canvas.bbox("all"))

            frame = tk.Frame(canvas)
            canvas.create_window((0, 0), window = frame, anchor = tk.NW)

            def on_mousewheel(event):
                
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

            canvas.bind_all("<MouseWheel>", on_mousewheel)

            bullish_divergences_list = []
            bearish_divergences_list = []

            for ticker, data in securities_data.items():
                bullish_divergences, bearish_divergences = detect_divergences(ticker, t_val, extrema_window_val, divergence_window_val, upper_barrier_val, lower_barrier_val, securities_data)

                if bullish_divergences:
                    for divergence in bullish_divergences:
                        start, end, span_days = divergence
                        bullish_divergences_list.append((ticker, span_days))

                if bearish_divergences:
                    for divergence in bearish_divergences:
                        start, end, span_days = divergence
                        bearish_divergences_list.append((ticker, span_days))

            if bullish_divergences_list:
                ttk.Label(frame, text = 'Bullish Divergences:', font = ('Helvetica', 12, 'bold')).pack(pady = (20, 10), padx = 20, anchor = 'w')

                for ticker, span_days in bullish_divergences_list:
                    ttk.Button(frame, text = f'{ticker} - {span_days} Days', command = lambda t = ticker: plot_graph(t, t_val, extrema_window_val, divergence_window_val, upper_barrier_val, lower_barrier_val, sma_short_val, sma_long_val, securities_data)).pack(anchor = 'w', padx = 20)

            if bearish_divergences_list:
                ttk.Label(frame, text = 'Bearish Divergences:', font = ('Helvetica', 12, 'bold')).pack(pady = (20, 10), padx = 20, anchor = 'w')

                for ticker, span_days in bearish_divergences_list:
                    ttk.Button(frame, text = f'{ticker} - {span_days} Days', command = lambda t = ticker: plot_graph(t, t_val, extrema_window_val, divergence_window_val, upper_barrier_val, lower_barrier_val, sma_short_val, sma_long_val, securities_data)).pack(anchor = 'w', padx = 20)
                    
            if not bullish_divergences_list and not bearish_divergences_list:
                ttk.Label(frame, text = 'No divergences detected within specified parameters.').pack(pady = 10)

            canvas.update_idletasks()
            canvas.config(scrollregion = canvas.bbox("all"))

        except ValueError as e:
            tk.messagebox.showerror("Input Error", f"Invalid input: {e}")


    root = tk.Tk()
    root.title("Divergence Detection")
    root.geometry('350x300')

    ttk.Label(root, text = "RSI Upper Barrier:").grid(row = 0, column = 0, padx = 10, pady = (20, 5))
    upper_barrier_entry = ttk.Entry(root)
    upper_barrier_entry.grid(row = 0, column = 1, padx = 10, pady = (20, 5))
    upper_barrier_entry.insert(0, "70")

    ttk.Label(root, text = "RSI Lower Barrier:").grid(row = 1, column = 0, padx = 10, pady = 5)
    lower_barrier_entry = ttk.Entry(root)
    lower_barrier_entry.grid(row = 1, column = 1, padx = 10, pady = 5)
    lower_barrier_entry.insert(0, "30")

    ttk.Label(root, text = "Short SMA Window:").grid(row = 2, column = 0, padx = 10, pady = 5)
    sma_short_entry = ttk.Entry(root)
    sma_short_entry.grid(row = 2, column = 1, padx = 10, pady = 5)
    sma_short_entry.insert(0, "14")

    ttk.Label(root, text = "Long SMA Window:").grid(row = 3, column = 0, padx = 10, pady = 5)
    sma_long_entry = ttk.Entry(root)
    sma_long_entry.grid(row = 3, column = 1, padx = 10, pady = 5)
    sma_long_entry.insert(0, "50")

    ttk.Label(root, text = "Extrema Window:").grid(row = 4, column = 0, padx = 10, pady = 5)
    extrema_window_entry = ttk.Entry(root)
    extrema_window_entry.grid(row = 4, column = 1, padx = 10, pady = 5)
    extrema_window_entry.insert(0, "2")

    ttk.Label(root, text = "Divergence Detection Window:").grid(row = 5, column = 0, padx = 10, pady = 5)
    divergence_window_entry = ttk.Entry(root)
    divergence_window_entry.grid(row = 5, column = 1, padx = 10, pady = 5)
    divergence_window_entry.insert(0, "30")

    ttk.Label(root, text = "T (Number of Days):").grid(row = 6, column = 0, padx = 10, pady = 5)
    t_entry = ttk.Entry(root)
    t_entry.grid(row = 6, column = 1, padx = 10, pady = 5)
    t_entry.insert(0, "30")

    show_divergences_button = ttk.Button(root, text = "Detect Divergences", command = show_divergences)
    show_divergences_button.grid(row = 7, column = 0, columnspan = 2, pady = 10)

    root.mainloop()

create_gui(securities_data)
