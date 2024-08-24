import yfinance as yf
import os
import pandas as pd
from functools import reduce
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Define the start and end dates
start_date = '2024-01-01'
end_date = pd.Timestamp.now().strftime('%Y-%m-%d')

# Download historical data for BTC from Yahoo Finance
btc_data = yf.download('BTC-USD', start=start_date, end=end_date)
ixs_data = yf.download('IXS-USD', start=start_date, end=end_date)
xrp_data = yf.download('XRP-USD', start=start_date, end=end_date)
csc_data = yf.download('CSC-USD', start=start_date, end=end_date)
sp500_data = yf.download('^GSPC', start=start_date, end=end_date)  # S&P 500 data


# Reset the index to include the date as a column
btc_data.reset_index(inplace=True)
ixs_data.reset_index(inplace=True)
xrp_data.reset_index(inplace=True)
csc_data.reset_index(inplace=True)
sp500_data.reset_index(inplace=True)

# Select the desired columns including the date
df_btc = btc_data[['Date', 'Close']]
df_btc = df_btc.rename(columns = {'Close':'BTC_Price'})

df_ixs = ixs_data[['Date', 'Close']]
df_ixs = df_ixs.rename(columns = {'Close':'IXS_Price'})

df_xrp = xrp_data[['Date', 'Close']]
df_xrp = df_xrp.rename(columns = {'Close':'XRP_Price'})

df_csc = csc_data[['Date', 'Close']]
df_csc = df_csc.rename(columns = {'Close':'CSC_Price'})

df_sp500 = sp500_data[['Date', 'Close']]
df_sp500 = df_sp500.rename(columns = {'Close':'SP500'})


#df_data = pd.merge(df_data, df_xrp, on = 'Date')

# List of DataFrames
dfs = [df_btc, df_ixs, df_xrp, df_csc, df_sp500]

# Use reduce to merge DataFrames
df_data = reduce(lambda left, right: pd.merge(left, right, on='Date'), dfs)

# Convert dates to string format - so it can be JSON serialized
df_data['Date'] = df_data['Date'].astype(str)

# Authentication
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'dashboardcrypto-431910-f1f9c1cf4069.json'
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, SERVICE_ACCOUNT_FILE)
creds = service_account.Credentials.from_service_account_file(script_path, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

SPREADSHEET_ID = '1XpFeYIow0_x4l7JBAUFQEAZ9m3QLiA9maCCfd7wmeuA'
RANGE_NAME = 'Sheet1'

# Convert the DataFrame to a list of lists for Google Sheets
values = [df_data.columns.tolist()] + df_data.values.tolist()

body = {
    'values': values
}

# Write in Google sheet
result = service.spreadsheets().values().update(
    spreadsheetId=SPREADSHEET_ID,
    range=RANGE_NAME,
    valueInputOption='RAW',
    body=body
).execute()


####### CSV
# Save the data to a CSV file
#csv_filename = 'btc_ixs_data_from_2024_with_dates.csv'
#df_data.to_csv(csv_filename, index=False, header=True)