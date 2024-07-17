
import pandas as pd
import stumpy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.style.use('https://raw.githubusercontent.com/TDAmeritrade/stumpy/main/docs/stumpy.mplstyle')

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

selected_security = 'SAN FP Equity'

m = 200  # Window size for STUMPY


def pattern_recognition(security, df):

    mp = stumpy.stump(df['Close'], m)
    motif_idx = np.argsort(mp[:, 0])[0]
    motif_date = df.index[motif_idx]
    
    nearest_neighbor_indices = np.argsort(mp[:, 0])[1:6]
    nearest_neighbors = [df.index[int(mp[idx, 1])] for idx in nearest_neighbor_indices]
    
    return motif_idx, motif_date, nearest_neighbor_indices, nearest_neighbors, mp


# PLOTTING


def plot_results(security, df, motif_idx, nearest_neighbor_indices, mp):
    fig, axs = plt.subplots(2, sharex = True, gridspec_kw = {'hspace': 0})
    plt.suptitle(f'Pattern Recognition for {security}', fontsize = 20)

    axs[0].plot(df['Close'].values)
    axs[0].set_ylabel('Close Prices', fontsize = 14)

    rect = Rectangle((motif_idx, df['Close'].min()), m, df['Close'].max() - df['Close'].min(), facecolor = 'lightgrey')
    axs[0].add_patch(rect)

    for idx in nearest_neighbor_indices:
        rect = Rectangle((int(mp[idx, 1]), df['Close'].min()), m, df['Close'].max() - df['Close'].min(), facecolor = 'lightgrey')
        axs[0].add_patch(rect)

    axs[1].set_xlabel('Time', fontsize = 14)
    axs[1].set_ylabel('Matrix Profile', fontsize = 14)
    axs[1].plot(mp[:, 0])

    for idx in nearest_neighbor_indices:
        axs[1].axvline(x = int(mp[idx, 1]), linestyle = "dashed", color = 'grey')

    axs[1].axvline(x = motif_idx, linestyle = "dashed", label = 'Motif', color = 'blue')
    axs[1].legend()

    plt.show()

if selected_security in securities_data:
    df = securities_data[selected_security]
    motif_idx, motif_date, nearest_neighbor_indices, nearest_neighbors, mp = pattern_recognition(selected_security, df)
    
    print(f"The motif date for {selected_security} is: {motif_date}")
    print(f"The next 5 nearest neighbors for {selected_security} are:")
    for neighbor in nearest_neighbors:
        print(f"Date: {neighbor}")
    
    plot_results(selected_security, df, motif_idx, nearest_neighbor_indices, mp)
else:
    print(f"Security '{selected_security}' not found in the loaded data.")
