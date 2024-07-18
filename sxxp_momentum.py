
import pandas as pd
import yfinance as yf
import tkinter as tk

from tkinter import scrolledtext
from dateutil.relativedelta import relativedelta

from data.sxxp_securities import sxxp_tickers

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 200)


ticker_data = {}
sxxp_df = pd.DataFrame()


def load_data():

    """
    Loads real-time price data from Yahoo Finance using YF library.
    """

    global ticker_data, sxxp_df

    for ticker in sxxp_tickers:
        data = yf.download(ticker, period = '1y', interval = '1d')['Adj Close']
        ticker_data[ticker] = data

    sxxp_df = pd.DataFrame(ticker_data)
    sxxp_df.index = pd.to_datetime(sxxp_df.index)


def get_top_earners_month(percentile: int):
    
    """
    Precondition: 0 < percentile <= 100
    
    Calculates the top percentile earners for the previous completed month based on adjusted close price.
    """
    
    global sxxp_df
    
    daily_returns = sxxp_df.pct_change()
    monthly_returns = daily_returns.resample('M').agg(lambda x: (x + 1).prod() - 1)
    
    most_recent_month = monthly_returns.index[-1]
    previous_month = most_recent_month - relativedelta(months = 1)
    
    if previous_month in monthly_returns.index:
        previous_month_returns = monthly_returns.loc[previous_month]
    
    else:
        closest_date = monthly_returns.index.to_series().apply(lambda x: abs(x - previous_month)).idxmin()
        previous_month_returns = monthly_returns.loc[closest_date]
    
    threshold = previous_month_returns.quantile(1 - percentile / 100.0)
    top_earners = previous_month_returns[previous_month_returns >= threshold]
    
    top_earners_df = top_earners.reset_index()
    top_earners_df.columns = ['Tickers', 'Returns']
    top_earners_df = top_earners_df.sort_values(by = 'Returns', ascending = False)
    
    return top_earners_df


def get_top_losers_month(percentile: int):

    """
    Precondition: 0 < percentile <= 100
    
    Calculates the top percentile losers for the previous completed month based on adjusted close price.
    """
    
    global sxxp_df
    
    daily_returns = sxxp_df.pct_change()
    monthly_returns = daily_returns.resample('M').agg(lambda x: (x + 1).prod() - 1)
    
    most_recent_month = monthly_returns.index[-1]
    previous_month = most_recent_month - relativedelta(months = 1)
    
    if previous_month in monthly_returns.index:
        previous_month_returns = monthly_returns.loc[previous_month]

    else:
        closest_date = monthly_returns.index.to_series().apply(lambda x: abs(x - previous_month)).idxmin()
        previous_month_returns = monthly_returns.loc[closest_date]
    
    threshold = previous_month_returns.quantile(percentile / 100.0)
    top_losers = previous_month_returns[previous_month_returns <= threshold]
    
    top_losers_df = top_losers.reset_index()
    top_losers_df.columns = ['Tickers', 'Returns']
    top_losers_df = top_losers_df.sort_values(by='Returns')
    
    return top_losers_df


def get_top_earners_week(percentile: int):
    
    """
    Precondition: 0 < percentile <= 100
    
    Calculates the top percentile earners for the previous completed week based on adjusted close price.
    """
    
    global sxxp_df
    
    daily_returns = sxxp_df.pct_change()
    weekly_returns = daily_returns.resample('W').agg(lambda x: (x + 1).prod() - 1)
    
    most_recent_week = weekly_returns.index[-1]
    previous_week = most_recent_week - relativedelta(weeks = 1)
    
    if previous_week in weekly_returns.index:
        previous_week_returns = weekly_returns.loc[previous_week]

    else:
        closest_date = weekly_returns.index.to_series().apply(lambda x: abs(x - previous_week)).idxmin()
        previous_week_returns = weekly_returns.loc[closest_date]
    
    threshold = previous_week_returns.quantile(1 - percentile / 100.0)
    top_earners = previous_week_returns[previous_week_returns >= threshold]
    
    top_earners_df = top_earners.reset_index()
    top_earners_df.columns = ['Tickers', 'Returns']
    top_earners_df = top_earners_df.sort_values(by = 'Returns', ascending = False)
    
    return top_earners_df


def get_top_losers_week(percentile: int):

    """
    Precondition: 0 < percentile <= 100
    
    Calculates the top percentile losers for the previous completed week based on adjusted close price.
    """

    global sxxp_df
    
    daily_returns = sxxp_df.pct_change()
    weekly_returns = daily_returns.resample('W').agg(lambda x: (x + 1).prod() - 1)
    
    most_recent_week = weekly_returns.index[-1]
    previous_week = most_recent_week - relativedelta(weeks=1)
    
    if previous_week in weekly_returns.index:
        previous_week_returns = weekly_returns.loc[previous_week]
   
    else:
        closest_date = weekly_returns.index.to_series().apply(lambda x: abs(x - previous_week)).idxmin()
        previous_week_returns = weekly_returns.loc[closest_date]
    
    threshold = previous_week_returns.quantile(percentile / 100.0)
    top_losers = previous_week_returns[previous_week_returns <= threshold]
    
    top_losers_df = top_losers.reset_index()
    top_losers_df.columns = ['Tickers', 'Returns']
    top_losers_df = top_losers_df.sort_values(by = 'Returns')
    
    return top_losers_df


def display_top_earners():

    """
    Displays and ranks top earners for the chosen period.
    """

    percentile = int(percentile_entry_earners.get())
    period = period_var_earners.get()

    if period == "Month":
        top_earners = get_top_earners_month(percentile)

    else:
        top_earners = get_top_earners_week(percentile)
    
    result_text = f"Top {percentile}% Earners (Previous {period}):\n"
    result_text += top_earners.to_string(index = False, float_format = "{:.2%}".format)
    text_area_earners.delete('1.0', tk.END)
    text_area_earners.insert(tk.END, result_text)


def display_top_losers():

    """
    Displays and ranks top losers for the chosen period.
    """

    percentile = int(percentile_entry_losers.get())
    period = period_var_losers.get()

    if period == "Month":
        top_losers = get_top_losers_month(percentile)
    
    else:
        top_losers = get_top_losers_week(percentile)
    
    result_text = f"Top {percentile}% Losers (Previous {period}):\n"
    result_text += top_losers.to_string(index = False, float_format = "{:.2%}".format)
    text_area_losers.delete('1.0', tk.END)
    text_area_losers.insert(tk.END, result_text)


# GUI WINDOW SETUP AND DESIGN


app = tk.Tk()
app.title("Momentum Trading GUI")

load_data()

frame_earners = tk.Frame(app)
frame_earners.pack(side = tk.TOP, padx = 10, pady = 10)

tk.Label(frame_earners, text = "Select Top Percentile of Earners:").pack(pady = 5)
percentile_entry_earners = tk.Entry(frame_earners)
percentile_entry_earners.pack(pady = 5)

period_frame_earners = tk.Frame(frame_earners)
period_frame_earners.pack(pady = 5)
period_var_earners = tk.StringVar(value = "Month")
tk.Radiobutton(period_frame_earners, text = "Previous Month", variable = period_var_earners, value = "Month").pack(side = tk.LEFT)
tk.Radiobutton(period_frame_earners, text = "Previous Week", variable = period_var_earners, value = "Week").pack(side = tk.LEFT)

display_button_earners = tk.Button(frame_earners, text = "Display Top Earners", command = display_top_earners)
display_button_earners.pack(pady = 10)

text_area_earners = scrolledtext.ScrolledText(frame_earners, wrap = tk.WORD, width = 80, height = 10)
text_area_earners.pack(padx = 10, pady = 10)

frame_losers = tk.Frame(app)
frame_losers.pack(side = tk.BOTTOM, padx = 10, pady = 10)

tk.Label(frame_losers, text = "Select Top Percentile of Losers:").pack(pady = 5)
percentile_entry_losers = tk.Entry(frame_losers)
percentile_entry_losers.pack(pady = 5)

period_frame_losers = tk.Frame(frame_losers)
period_frame_losers.pack(pady = 5)
period_var_losers = tk.StringVar(value = "Month")
tk.Radiobutton(period_frame_losers, text = "Previous Month", variable = period_var_losers, value = "Month").pack(side = tk.LEFT)
tk.Radiobutton(period_frame_losers, text = "Previous Week", variable = period_var_losers, value = "Week").pack(side = tk.LEFT)

display_button_losers = tk.Button(frame_losers, text = "Display Top Losers", command = display_top_losers)
display_button_losers.pack(pady = 10)

text_area_losers = scrolledtext.ScrolledText(frame_losers, wrap = tk.WORD, width = 80, height = 10)
text_area_losers.pack(padx = 10, pady = 10)

app.mainloop()

