
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

from ta.trend import SMAIndicator

import tkinter as tk
from tkinter import ttk

from data.sxxp_securities import sxxp_tickers

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 200)


securities_data = {}

for ticker in sxxp_tickers:
    try:
        data = yf.download(ticker, period = '1y', interval = '1d')
        if not data.empty:
            securities_data[ticker] = data

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")


def calculate_sma_and_crossover(securities_data):
    
    crossover_securities = {}

    for ticker, df in securities_data.items():
        indicator_sma = SMAIndicator(df['Adj Close'], window = 141, fillna = False)
        df['SMA141'] = indicator_sma.sma_indicator()
        df['Prev_Adj_Close'] = df['Adj Close'].shift(1)
        df['Prev_SMA141'] = df['SMA141'].shift(1)

        df['Crossover'] = ((df['Prev_Adj_Close'] < df['Prev_SMA141']) & (df['Adj Close'] > df['SMA141'])).astype(int) - \
                          ((df['Prev_Adj_Close'] > df['Prev_SMA141']) & (df['Adj Close'] < df['SMA141'])).astype(int)

        crossover_df = df[df['Crossover'] != 0]
        if not crossover_df.empty:
            recent_crossover = crossover_df.iloc[-1]
            crossover_type = 'over' if recent_crossover['Crossover'] == 1 else 'under'
            crossover_date = recent_crossover.name
            crossover_securities[ticker] = (crossover_type, crossover_date)

    return crossover_securities

crossover_securities = calculate_sma_and_crossover(securities_data)


class CrossoverApp(tk.Tk):

    def __init__(self, crossover_securities, securities_data):
       
        super().__init__()

        self.crossover_securities = crossover_securities
        self.securities_data = securities_data
        self.title("Crossover Securities")
        self.geometry("600x400")

        self.tree = ttk.Treeview(self, columns = ("Security", "Crossover", "Date"), show = 'headings')
        self.tree.heading("Security", text = "Security")
        self.tree.heading("Crossover", text = "Crossover")
        self.tree.heading("Date", text = "Date")
        self.tree.pack(fill = tk.BOTH, expand = True)

        for ticker, (crossover_type, crossover_date) in self.crossover_securities.items():
            self.tree.insert("", "end", values = (ticker, crossover_type, crossover_date))

        self.tree.bind("<Double-1>", self.on_double_click)


    def on_double_click(self, event):

        item = self.tree.selection()[0]
        ticker = self.tree.item(item, "values")[0]
        self.plot_security(ticker, self.securities_data[ticker])


    def plot_security(self, ticker, df):

        plt.figure(figsize = (14, 7))
        plt.plot(df.index, df['Adj Close'], label = 'Adjusted Close Price')
        plt.plot(df.index, df['SMA141'], label = 'SMA141', alpha = 0.7)
        plt.title(f"{ticker} Price and SMA141")

        crossover_type, crossover_date = self.crossover_securities[ticker]
        color = 'green' if crossover_type == 'over' else 'red'
        plt.scatter([crossover_date], [df.loc[crossover_date, 'Adj Close']], color = color, marker = '^' if crossover_type == 'over' else 'v', s = 100)

        plt.legend()
        plt.show()

app = CrossoverApp(crossover_securities, securities_data)
app.mainloop()
