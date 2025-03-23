import pandas as pd
import yfinance as yf
import gspread
import os
from datetime import datetime, timedelta
from pytrends.request import TrendReq
from google.oauth2 import service_account
from gspread_dataframe import set_with_dataframe

# Google Sheets authentication setup
SERVICE_ACCOUNT_FILE = 'dashboardcrypto-431910-f1f9c1cf4069.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, SERVICE_ACCOUNT_FILE)
creds = service_account.Credentials.from_service_account_file(script_path, scopes=SCOPES)
client = gspread.authorize(creds)

# Google Sheets setup
SPREADSHEET_ID = '1NcBARP6HAUQYepIvXWLciVmxZ-FKRq16k0HgXwlyn2o'
BTC_PRICE_SHEET = 'btc_price'
BTC_TREND_SHEET = 'btc_trend'
OUTPUT_SHEET = 'Sheet1'

# Define date range
num_days = 30
end_date = datetime.today()
start_date = end_date - timedelta(days=num_days)
trend_start_date = start_date - timedelta(days=1)
trend_end_date = end_date - timedelta(days=1)

# Open spreadsheet
output_spreadsheet = client.open_by_key(SPREADSHEET_ID)

# Clear existing data in btc_price and btc_trend sheets
btc_price_worksheet = output_spreadsheet.worksheet(BTC_PRICE_SHEET)
btc_trend_worksheet = output_spreadsheet.worksheet(BTC_TREND_SHEET)
btc_price_worksheet.clear()
btc_trend_worksheet.clear()
print("Cleared btc_price and btc_trend sheets.")

# Step 1: Fetch BTC price and store in 'btc_price'
btc_data = yf.download('BTC-USD', start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
btc_data = btc_data[['Close']].reset_index()
btc_data.rename(columns={'Date': 'date', 'Close': 'btc_price'}, inplace=True)
set_with_dataframe(btc_price_worksheet, btc_data)
print("BTC price data inserted into btc_price tab.")

# Step 2: Fetch Google Trends data for Bitcoin and Crypto
pytrends = TrendReq(hl='en-US', tz=360)
pytrends.build_payload(['Bitcoin', 'Crypto'], timeframe=f'{trend_start_date.strftime("%Y-%m-%d")} {trend_end_date.strftime("%Y-%m-%d")}', geo='', gprop='')
trends_df = pytrends.interest_over_time().drop(columns=['isPartial'], errors='ignore').reset_index()
trends_df.rename(columns={'date': 'date', 'Bitcoin': 'BTC_trend', 'Crypto': 'Crypto_trend'}, inplace=True)
set_with_dataframe(btc_trend_worksheet, trends_df)
print("BTC and Crypto trend data inserted into btc_trend tab.")

# Step 3: Merge data from btc_price and btc_trend, then store in 'Sheet1'
btc_price_df = pd.DataFrame(btc_price_worksheet.get_all_records())
btc_trend_df = pd.DataFrame(btc_trend_worksheet.get_all_records())
btc_trend_df['date'] = pd.to_datetime(btc_trend_df['date'])
btc_price_df['date'] = pd.to_datetime(btc_price_df['date'])
merged_df = btc_price_df.merge(btc_trend_df, on='date', how='left')
output_worksheet = output_spreadsheet.worksheet(OUTPUT_SHEET)
set_with_dataframe(output_worksheet, merged_df)
print("Merged data inserted into Sheet1 tab.")
