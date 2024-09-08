import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

# Your FRED API key
fred_api_key = 'a963de8eb5063f6bf00f1869f3fecf9f'

# Define the FRED API URLs
inflation_url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCNS&api_key={fred_api_key}&file_type=json"
unemployment_url = f"https://api.stlouisfed.org/fred/series/observations?series_id=UNRATE&api_key={fred_api_key}&file_type=json"
interest_rate_url = f"https://api.stlouisfed.org/fred/series/observations?series_id=FEDFUNDS&api_key={fred_api_key}&file_type=json"
debt_url = f"https://api.stlouisfed.org/fred/series/observations?series_id=GFDEBTN&api_key={fred_api_key}&file_type=json"  # US Federal Debt
savings_rate_url = f"https://api.stlouisfed.org/fred/series/observations?series_id=PSAVERT&api_key={fred_api_key}&file_type=json"  # Personal Savings Rate

# Define parameters to get data from January 1, 2020 to the current date
start_date = '2020-01-01'
end_date = datetime.now().strftime('%Y-%m-%d')

params = {
    'format': 'json',
    'frequency': 'm',  # Monthly frequency
    'start_date': start_date,
    'end_date': end_date
}

# Function to get data from the API
def get_data(url, params):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'observations' in data:
            df = pd.DataFrame(data['observations'])
            return df
    return pd.DataFrame()

# Get data for inflation, unemployment, interest rate, debt, and savings rate
inflation_data = get_data(inflation_url, params)
unemployment_data = get_data(unemployment_url, params)
interest_rate_data = get_data(interest_rate_url, params)
debt_data = get_data(debt_url, params)
savings_rate_data = get_data(savings_rate_url, params)

# Convert date to datetime format and value to numeric for all datasets
for data in [inflation_data, unemployment_data, interest_rate_data, debt_data, savings_rate_data]:
    data['date'] = pd.to_datetime(data['date'])
    data['value'] = pd.to_numeric(data['value'], errors='coerce')

# Filter data from January 1, 2020 onwards and sort by date
for data in [inflation_data, unemployment_data, interest_rate_data, debt_data, savings_rate_data]:
    data = data[data['date'] >= pd.to_datetime(start_date)]
    data.sort_values(by='date', inplace=True)

# Calculate monthly inflation rates
inflation_data['Previous_CPI'] = inflation_data['value'].shift(1)
inflation_data['Inflation_rate'] = ((inflation_data['value'] - inflation_data['Previous_CPI']) / inflation_data['Previous_CPI']) * 100
inflation_data.dropna(inplace=True)

# Merge inflation, unemployment, interest rate, debt, and savings rate data on the date column
merged_data = pd.merge(inflation_data[['date', 'value', 'Inflation_rate']], unemployment_data[['date', 'value']], on='date', how='inner', suffixes=('_CPI', '_UNRATE'))
merged_data = pd.merge(merged_data, interest_rate_data[['date', 'value']], on='date', how='inner')
merged_data = pd.merge(merged_data, debt_data[['date', 'value']], on='date', how='inner')
merged_data = pd.merge(merged_data, savings_rate_data[['date', 'value']], on='date', how='inner')

# Rename columns
merged_data.columns = ['Date', 'CPI', 'Inflation_rate', 'Unemployment_rate', 'Interest_rate', 'Debt', 'Savings_rate']

# Standardize the date format to YYYY-MM-DD
merged_data['Date'] = merged_data['Date'].dt.strftime('%Y-%m-%d')

# Set up Google Sheets connection
current_dir = os.path.dirname(os.path.abspath(__file__))
service_account_file = os.path.join(current_dir, 'dashboardcrypto-431910-f1f9c1cf4069.json')
spreadsheet_id = '1tgkiZzKp4m9sBOhjvj_3nvlvYJ4N8W9INGn7wFh8a4o'
range_name = 'Sheet1'

# Set up Google Sheets API client
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_file, scope)
client = gspread.authorize(creds)

# Open the Google Sheet
spreadsheet = client.open_by_key(spreadsheet_id)
sheet = spreadsheet.worksheet(range_name)

# Clear the sheet before writing new data
sheet.clear()

# Set the headers
sheet.append_row(merged_data.columns.tolist())

# Write the data to the sheet
for row in merged_data.values.tolist():
    sheet.append_row(row)
