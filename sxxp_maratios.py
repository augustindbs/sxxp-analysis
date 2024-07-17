
import pandas as pd
import yfinance as yf
import tkinter as tk

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
    result_text += top_ratio.to_string(index=False)
    text_area_ratio.delete('1.0', tk.END)
    text_area_ratio.insert(tk.END, result_text)


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

app.mainloop()
