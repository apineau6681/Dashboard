import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

# Your FRED API key
fred_api_key = os.getenv("FRED_API_KEY")

# Define the FRED API URLs
inflation_url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCNS&api_key={fred_api_key}&file_type=json"
unemployment_url = f"https://api.stlouisfed.org/fred/series/observations?series_id=UNRATE&api_key={fred_api_key}&file_type=json"
interest_rate_url = f"https://api.stlouisfed.org/fred/series/observations?series_id=FEDFUNDS&api_key={fred_api_key}&file_type=json"
savings_rate_url = f"https://api.stlouisfed.org/fred/series/observations?series_id=PSAVERT&api_key={fred_api_key}&file_type=json"

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
            # Check if required columns exist
            if 'date' in df.columns and 'value' in df.columns:
                print(f"Data for {url}: Columns are present.")
            else:
                print(f"Data for {url}: Columns missing. Available columns: {df.columns.tolist()}")
            return df
    return pd.DataFrame()

# Get data
inflation_data = get_data(inflation_url, params)
unemployment_data = get_data(unemployment_url, params)
interest_rate_data = get_data(interest_rate_url, params)
savings_rate_data = get_data(savings_rate_url, params)

# Function to ensure data has 'date' and 'value' columns
def ensure_columns(data, label):
    if 'date' not in data.columns or 'value' not in data.columns:
        print(f"Data for {label} does not contain required columns. Columns present: {data.columns.tolist()}")
        raise ValueError(f"Expected columns 'date' and 'value' are missing in the {label} data.")

# Ensure all datasets have the required columns
for data, label in [(inflation_data, 'Inflation'), (unemployment_data, 'Unemployment'), 
                    (interest_rate_data, 'Interest Rate'), (savings_rate_data, 'Savings Rate')]:
    ensure_columns(data, label)

# Convert 'date' to datetime format and 'value' to numeric
def convert_data(data):
    data['date'] = pd.to_datetime(data['date'])
    data['value'] = pd.to_numeric(data['value'], errors='coerce')
    return data

# Apply conversion
inflation_data = convert_data(inflation_data)
unemployment_data = convert_data(unemployment_data)
interest_rate_data = convert_data(interest_rate_data)
savings_rate_data = convert_data(savings_rate_data)

# Filter and sort data
def filter_and_sort(data):
    data = data[data['date'] >= pd.to_datetime(start_date)]
    return data.sort_values(by='date')

# Apply filtering and sorting
inflation_data = filter_and_sort(inflation_data)
unemployment_data = filter_and_sort(unemployment_data)
interest_rate_data = filter_and_sort(interest_rate_data)
savings_rate_data = filter_and_sort(savings_rate_data)

# Calculate monthly inflation rates
inflation_data['Previous_CPI'] = inflation_data['value'].shift(1)
inflation_data['Inflation_rate'] = ((inflation_data['value'] - inflation_data['Previous_CPI']) / inflation_data['Previous_CPI']) * 100
inflation_data.dropna(inplace=True)

# Merge datasets
merged_data = pd.merge(inflation_data[['date', 'value', 'Inflation_rate']], 
                       unemployment_data[['date', 'value']], 
                       on='date', how='inner', suffixes=('_CPI', '_UNRATE'))
merged_data = pd.merge(merged_data, interest_rate_data[['date', 'value']], on='date', how='inner')
merged_data = pd.merge(merged_data, savings_rate_data[['date', 'value']], on='date', how='inner')

# Rename columns
merged_data.columns = ['Date', 'CPI', 'Inflation_rate', 'Unemployment_rate', 'Interest_rate', 'Savings_rate']

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
