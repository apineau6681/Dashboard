import yfinance as yf
import matplotlib.pyplot as plt
from pandas.plotting._matplotlib.style import get_standard_colors
from functools import reduce
import pandas as pd

# Define the start and end dates
start_date = '2024-03-01'
end_date = pd.Timestamp.now().strftime('%Y-%m-%d')

# Download historical data for BTC from Yahoo Finance
btc_data = yf.download('BTC-USD', start=start_date, end=end_date)
ixs_data = yf.download('IXS-USD', start=start_date, end=end_date)
#xrp_data = yf.download('XRP-USD', start=start_date, end=end_date)
#csc_data = yf.download('CSC-USD', start=start_date, end=end_date)
sol_data = yf.download('SOL-USD', start=start_date, end=end_date)
sui_data = yf.download('SUI-USD', start=start_date, end=end_date)

# Reset the index to include the date as a column
btc_data.reset_index(inplace=True)
ixs_data.reset_index(inplace=True)
#xrp_data.reset_index(inplace=True)
#csc_data.reset_index(inplace=True)
sol_data.reset_index(inplace=True)
sui_data.reset_index(inplace=True)

# Select the desired columns including the date
df_btc = btc_data[['Date', 'Close']]
df_btc = df_btc.rename(columns = {'Close':'BTC_Price'})

df_ixs = ixs_data[['Date', 'Close']]
df_ixs = df_ixs.rename(columns = {'Close':'IXS_Price'})

#df_xrp = xrp_data[['Date', 'Close']]
#df_xrp = df_xrp.rename(columns = {'Close':'XRP_Price'})

#df_csc = csc_data[['Date', 'Close']]
#df_csc = df_csc.rename(columns = {'Close':'CSC_Price'})

df_sol = sol_data[['Date', 'Close']]
df_sol = df_sol.rename(columns = {'Close':'SOL_Price'})

df_sui = sui_data[['Date', 'Close']]
df_sui = df_sui.rename(columns = {'Close':'SUI_Price'})

#df_data = pd.merge(df_data, df_xrp, on = 'Date')

# List of DataFrames
dfs = [df_btc, df_ixs, df_sol, df_sui]

# Use reduce to merge DataFrames
df_data = reduce(lambda left, right: pd.merge(left, right, on='Date'), dfs)

print(df_data)

# Save the data to a CSV file
csv_filename = 'btc_ixs_data_from_2024_with_dates.csv'
df_data.to_csv(csv_filename, index=False, header=True)

print(f"The data has been saved to {csv_filename}")

#plot the data
#import matplotlib.pyplot as plt

def plot_multi(data, date_col='Date', cols=None, spacing=.1, **kwargs):

    # Convert date column to datetime
    data[date_col] = pd.to_datetime(data[date_col])

    # Get default color style from pandas - can be changed to any other color list
    if cols is None: cols = data.columns
    if len(cols) == 0: return
    colors = get_standard_colors(num_colors=len(cols))

    # First axis
    ax = data.loc[:, cols[0]].plot(x='Date', y=cols[0], label=cols[0], color=colors[0], **kwargs)
    ax.set_ylabel(ylabel=cols[0])
    lines, labels = ax.get_legend_handles_labels()

    #ax = data.plot(x=date_col, y=cols[0], label=cols[0], color=colors[0], **kwargs)
    #ax.set_ylabel(cols[0])
    #lines, labels = ax.get_legend_handles_labels()

    for n in range(1, len(cols)):
        # Multiple y-axes
        ax_new = ax.twinx()
        ax_new.spines['right'].set_position(('axes', 1 + spacing * (n - 1)))
        data.loc[:, cols[n]].plot(ax=ax_new, label=cols[n], color=colors[n % len(colors)], **kwargs)
        ax_new.set_ylabel(ylabel=cols[n])
        
        # Proper legend position
        line, label = ax_new.get_legend_handles_labels()
        lines += line
        labels += label

    ax.legend(lines, labels, loc=0)
    return ax

plot_multi(df_data, date_col='Date', figsize=(10, 5))

def plot_multi2(data, date_col='Date', cols=None, spacing=.1, **kwargs):
    """
    Plots multiple columns against a date column with different y-axes.

    Parameters:
    - data: DataFrame with at least one date column and multiple columns to plot.
    - date_col: The name of the column containing date values.
    - cols: List of column names to plot. If None, all columns except date_col are plotted.
    - spacing: Spacing between y-axes for multiple y-axes.
    - kwargs: Additional keyword arguments passed to the plot function.
    """
    
    # Convert date column to datetime
    data[date_col] = pd.to_datetime(data[date_col])
    
    # Get default color style from pandas - can be changed to any other color list
    if cols is None:
        cols = [col for col in data.columns if col != date_col]
    if len(cols) == 0:
        return
    
    colors = plt.get_cmap('tab10').colors  # Use a colormap for colors

    # First axis
    ax = data.plot(x=date_col, y=cols[0], label=cols[0], color=colors[0], **kwargs)
    ax.set_ylabel(cols[0])
    lines, labels = ax.get_legend_handles_labels()

    for n in range(1, len(cols)):
        # Multiple y-axes
        ax_new = ax.twinx()
        ax_new.spines['right'].set_position(('axes', 1 + spacing * (n - 1)))
        data.plot(x=date_col, y=cols[n], ax=ax_new, label=cols[n], color=colors[n % len(colors)], **kwargs)
        ax_new.set_ylabel(cols[n])
        ax_new.get_legend().remove()
        
        # Proper legend position
        line, label = ax_new.get_legend_handles_labels()
        lines += line
        labels += label


    plt.xlabel(date_col)  # Set x-axis label as date column name
    # Ajuster la mise en page pour aligner le graphique à gauche
    plt.subplots_adjust(left=0.1, right=0.8, top=0.9, bottom=0.1)
    ax.legend(lines, labels, loc=0)
    plt.show()  # Show the plot
    return ax

#plot_multi(btc_ixs_data, figsize=(10, 5))
plot_multi2(df_data, date_col='Date', figsize=(15, 5))
