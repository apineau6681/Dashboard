import pandas as pd
import matplotlib.pyplot as plt
from pytrends.request import TrendReq
from datetime import datetime
import yfinance as yf
import gspread
import os
from google.oauth2 import service_account
from gspread_dataframe import set_with_dataframe

# Google Sheets authentication setup
SERVICE_ACCOUNT_FILE = 'dashboardcrypto-431910-f1f9c1cf4069.json'  # Path to your service account credentials JSON file
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, SERVICE_ACCOUNT_FILE)
creds = service_account.Credentials.from_service_account_file(script_path, scopes=SCOPES)
client = gspread.authorize(creds)

# Define the Google Sheet ID and the worksheet name
SPREADSHEET_ID = '1zbt6dJpB8xHPkMxJ4e03shLxNRAhvlPwy3Qe4YKY7tw'
WORKSHEET_NAME = 'Sheet1'  # Name of the worksheet where you want to write the data

# Initialize pytrends object
pytrends = TrendReq(hl='en-US', tz=360)

# Define the search terms
search_terms = ["Bitcoin", "XRP", "Crypto"]

# Define the start date and end date
start_date = '2020-01-01'  # Start date in 'YYYY-MM-DD' format
end_date = datetime.today().strftime('%Y-%m-%d')  # End date as today's date in 'YYYY-MM-DD' format

# Build the payload for Google Trends
timeframe = f'{start_date} {end_date}'
pytrends.build_payload(search_terms, cat=0, timeframe=timeframe, geo='', gprop='')

# Retrieve interest over time data
trends_df = pytrends.interest_over_time()

# Drop 'isPartial' column if exists
if 'isPartial' in trends_df.columns:
    trends_df = trends_df.drop(columns=['isPartial'])

# Fetch BTC Close Price using yfinance
btc_data = yf.download('BTC-USD', start=start_date, end=end_date)
xrp_data = yf.download('XRP-USD', start=start_date, end=end_date)
btc_close_prices = btc_data[['Close']]
xrp_close_prices = xrp_data[['Close']]
btc_close_prices.rename(columns={'Close': 'BTC_Price'}, inplace=True)
xrp_close_prices.rename(columns={'Close': 'XRP_Price'}, inplace=True)

# Merge BTC close prices with Google Trends data
combined_btc_df = trends_df.join(btc_close_prices, how='inner')
combined_df = combined_btc_df.join(xrp_close_prices, how='inner')


# Reset the index to include the 'Date' as a column
combined_df.reset_index(inplace=True)
# Rename the 'index' column to 'Date'
combined_df.rename(columns={'index': 'Date'}, inplace=True)
#combined_df['Date'] = combined_df['Date'].astype(str)

# Access the output Google Sheet and write the DataFrame
output_spreadsheet = client.open_by_key(SPREADSHEET_ID)
output_worksheet = output_spreadsheet.worksheet(WORKSHEET_NAME)
set_with_dataframe(output_worksheet, combined_df, include_index=True, include_column_header=True)
print("Data has been successfully read from the input Google Sheet and written to the output Google Sheet.")

###### CSV
#print(f'Data saved to Google Sheet: {spreadsheet_name}")
#path = './google_trends.csv'
#combined_df.to_csv(path, index_label='index')

###### Optional: Plot the data
#plt.figure(figsize=(12, 8))
#ax = combined_df.plot(secondary_y=['Close'], title='Google Trends and BTC Close Price')
#ax.set_ylabel('Google Trends Interest')
#ax.right_ax.set_ylabel('BTC Close Price (USD)')
#plt.grid(True)
#plt.show()
