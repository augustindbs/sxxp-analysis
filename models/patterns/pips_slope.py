
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


sxxp = pd.ExcelFile('main/data/sxxp_daily.xlsx')
securities_data = {}
securities = sxxp.sheet_names

for security in securities:
    path = f"main/data/pkl/{security}.pkl"
    securities_data[security] = pd.read_pickle(path)

# Weekly price data resampling
start_date = '2014-01-10'

securities_weekly_data = {}

for security, df in securities_data.items():
    weekly_df = df.resample('W-FRI', closed = 'right', label = 'right').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum',
    })

    weekly_df.dropna(inplace=True)

    weekly_df = weekly_df[start_date:]

    securities_weekly_data[security] = weekly_df

# Monthly price data resampling
start_date = '2014-01-01'

securities_monthly_data = {}

for security, df in securities_data.items():
    monthly_df = df.resample('MS', closed = 'right', label = 'right').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum',
    })

    monthly_df.dropna(inplace = True)

    monthly_df = monthly_df[start_date:]

    securities_monthly_data[security] = monthly_df


def find_pips(data: np.ndarray, n_pips: int, dist_measure: int):
   
    """
    Finds perceptually important points (pips) to approximate stock movements with straight lines.
    """

    # Adjust dist_measure to select which type to use
        # 1 = Euclidean Distance
        # 2 = Perpendicular Distance
        # 3 = Vertical Distance
    
    pips_x = [0, len(data) - 1] 
    pips_y = [data[0], data[-1]]

    for current_point in range(2, n_pips):
        md = 0.0  
        md_i = -1 
        insert_index = -1

        for k in range(0, current_point - 1):
            left_adj = k
            right_adj = k + 1

            time_diff = pips_x[right_adj] - pips_x[left_adj]
            price_diff = pips_y[right_adj] - pips_y[left_adj]
            slope = price_diff / time_diff
            intercept = pips_y[left_adj] - pips_x[left_adj] * slope

            for i in range(pips_x[left_adj] + 1, pips_x[right_adj]):
                
                d = 0.0

                if dist_measure == 1:  # Euclidean distance
                    d = ((pips_x[left_adj] - i) ** 2 + (pips_y[left_adj] - data[i]) ** 2) ** 0.5
                    d += ((pips_x[right_adj] - i) ** 2 + (pips_y[right_adj] - data[i]) ** 2) ** 0.5

                elif dist_measure == 2:  # Perpendicular distance
                    d = abs((slope * i + intercept) - data[i]) / (slope ** 2 + 1) ** 0.5
                    
                else:  # Vertical distance
                    d = abs((slope * i + intercept) - data[i])

                if d > md:
                    md = d
                    md_i = i
                    insert_index = right_adj

        pips_x.insert(insert_index, md_i)
        pips_y.insert(insert_index, data[md_i])

    return pips_x, pips_y


def detect_steep_slopes(pips_x, pips_y, slope_threshold_factor, price_change_threshold): 
   
    """
    Calculates the gradient between each pair of PIPs found and computes the average of the absolute values of these slopes.
    
    Threshold for steep slopes is determined by multipyling the slope_threshold_factor with the average slope.

    Algorithm identifies slope as steep if the absolute value of any slope exceeds the threshold and if the price change exceeds the price change threshold.
    """

    slopes = []
    price_changes = []
    
    for i in range(len(pips_x) - 1):
        time_diff = pips_x[i + 1] - pips_x[i]
        price_diff = pips_y[i + 1] - pips_y[i]
        slope = price_diff / time_diff
        slopes.append(slope)
        price_changes.append(abs(price_diff))

    avg_slope = np.mean(np.abs(slopes))
    avg_price = np.mean(pips_y)
    
    steep_slopes = [i for i, (slope, price_change) in enumerate(zip(slopes, price_changes))
                    if (np.abs(slope) > slope_threshold_factor * avg_slope) and 
                       (price_change > price_change_threshold * avg_price)]
    
    return steep_slopes

#--------------------------------------------------------------------------------------------------------------------------------------------------


security = random.choice(securities)
frequency = 'Daily'  

if frequency == 'Daily':
    df = securities_data[security]
    data = df['Close'][-2000:].values
elif frequency == 'Weekly':
    df = securities_weekly_data[security]
    data = df['Close'][-100:].values
elif frequency == 'Monthly':
    df = securities_monthly_data[security]
    data = df['Close'][-10:].values

slope_threshold_factor = 0.1
price_change_threshold = 0.2 
n_pips_list = [50, 100, 150, 200]


#--------------------------------------------------------------------------------------------------------------------------------------------------


# PLOTTING


plt.style.use('dark_background')
fig, axs = plt.subplots(len(n_pips_list), 1, figsize = (12, 12))

for idx, n_pips in enumerate(n_pips_list):
    pips_x, pips_y = find_pips(data, n_pips, 3) # Modify which type of distance calculation to use (1, 2, 3)
    steep_slope_indices = detect_steep_slopes(pips_x, pips_y, slope_threshold_factor, price_change_threshold)
    
    axs[idx].plot(data, label = 'Stock Data', color = 'white', alpha = 0.9, linewidth = 0.75)

    for i in range(len(pips_x) - 1):
        color = 'magenta' if i in steep_slope_indices else 'cyan'
        linewidth = 3 if i in steep_slope_indices else 1
        axs[idx].plot([pips_x[i], pips_x[i + 1]], [pips_y[i], pips_y[i + 1]], color = color, linestyle = '-', linewidth = linewidth, alpha = 0.75)
    
    axs[idx].set_xlabel('Index', color = 'white')
    axs[idx].set_ylabel('Close Price', color = 'white')
    axs[idx].set_title(f'Pivotal Points Detection with Steep Slopes ({n_pips} PIPs)', color = 'white')
    axs[idx].grid(True, color = 'gray')

plt.tight_layout()
plt.subplots_adjust(hspace = 0.5)

plt.show()
