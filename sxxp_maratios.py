
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from tkinter import scrolledtext
from ta.trend import SMAIndicator

from data.sxxp_securities import sxxp_tickers

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 200)


securities_data = {}

for ticker in sxxp_tickers:
    data = yf.download(ticker, period = '1y', interval = '1d')
    securities_data[ticker] = data

for ticker, df in securities_data.items():
    indicator_sma = SMAIndicator(df['Adj Close'], window = 141, fillna = True)
    df['SMA141'] = indicator_sma.sma_indicator()
    df['Ratio'] = df['Adj Close'] / df['SMA141']
    securities_data[ticker] = df


def get_top_ratio(percentile: int):

    """
    Precondition: 0 < percentile <= 100

    Ranks STOXX 600 equities by their Ratio on the last recorded trading day, i.e. the relative distance to their 141-day simple moving average.
    """
    
    last_day_ratios = {}

    for ticker, df in securities_data.items():
        last_day_ratio = df['Ratio'].iloc[-1]
        last_day_ratios[ticker] = last_day_ratio

    ratios_df = pd.DataFrame(list(last_day_ratios.items()), columns = ['Ticker', 'Ratio'])

    threshold = ratios_df['Ratio'].quantile(1 - percentile / 100.0)

    top_ratios_df = ratios_df[ratios_df['Ratio'] >= threshold]

    top_ratios_df = top_ratios_df.sort_values(by = 'Ratio', ascending = False).reset_index(drop = True)

    return top_ratios_df


def display_top_ratio():

    """
    Displays and ranks top earners for the chosen percentile.
    """

    percentile = int(percentile_entry_ratio.get())
    top_ratio = get_top_ratio(percentile)
    result_text = f"Top {percentile}% SMA141 Ratios:\n"
    result_text += top_ratio.to_string(index = False)
    text_area_ratio.delete('1.0', tk.END)
    text_area_ratio.insert(tk.END, result_text)


def display_all_ratio():

    """
    Displays the ranked list of all securities in the STOXX 600.
    """

    percentile = 100
    top_ratio = get_top_ratio(percentile)
    result_text = "All SMA141 Ratios:\n"
    result_text += top_ratio.to_string(index = False)
    text_area_ratio.delete('1.0', tk.END)
    text_area_ratio.insert(tk.END, result_text)


def plot_graph(ticker):
    
    """
    Plots the adjusted close price and the SMA141 on the same graph.
    """

    df = securities_data[ticker]
   
    fig, ax = plt.subplots(figsize = (10, 5))
    ax.plot(df.index, df['Adj Close'], label = 'Adj Close', color = 'black', alpha = 0.9, linewidth = 0.75)
    ax.plot(df.index, df['SMA141'], label = 'SMA141', color = 'magenta', alpha = 0.9, linewidth = 0.75)
    ax.set_title(f'{ticker} - Adj Close and SMA141')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.grid(True, color = 'gray', alpha = 0.2)
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master = frame_graph_plot)
    canvas.draw()
    canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)


def display_graph():
   
    """
    Displays the graph for the selected ticker.
    """

    ticker = ticker_entry.get().strip().upper()
    
    if ticker in securities_data:
        for widget in frame_graph_plot.winfo_children():
            widget.destroy()
        plot_graph(ticker)

    else:
        text_area_ratio.delete('1.0', tk.END)
        text_area_ratio.insert(tk.END, f"Ticker {ticker} not found in the data.")


# GUI WINDOW SETUP AND DESIGN


app = tk.Tk()
app.title("SMA141 Ratio GUI")

frame_ratio = tk.Frame(app)
frame_ratio.pack(side = tk.TOP, padx = 10, pady = 10)

tk.Label(frame_ratio, text = "Select Percentile:").pack(pady = 5)
percentile_entry_ratio = tk.Entry(frame_ratio)
percentile_entry_ratio.pack(pady = 5)

button_frame = tk.Frame(frame_ratio)
button_frame.pack(pady = 10)

display_button_ratio = tk.Button(button_frame, text = "Display Top Ratios", command = display_top_ratio)
display_button_ratio.pack(side = tk.LEFT, padx = 5)

display_button_all = tk.Button(button_frame, text = "Display All", command = display_all_ratio)
display_button_all.pack(side = tk.LEFT, padx = 5)

text_area_ratio = scrolledtext.ScrolledText(frame_ratio, wrap = tk.WORD, width = 80, height = 10)
text_area_ratio.pack(padx = 10, pady = 10)

frame_graph_controls = tk.Frame(app)
frame_graph_controls.pack(side = tk.TOP, padx = 10, pady = 10)

tk.Label(frame_graph_controls, text="Enter Ticker:").pack(pady = 5)
ticker_entry = tk.Entry(frame_graph_controls)
ticker_entry.pack(pady = 5)

display_button_graph = tk.Button(frame_graph_controls, text = "Display Graph", command = display_graph)
display_button_graph.pack(pady = 5)

frame_graph_plot = tk.Frame(app)
frame_graph_plot.pack(side = tk.TOP, fill = tk.BOTH, expand = True, padx = 10, pady = 10)

app.mainloop()