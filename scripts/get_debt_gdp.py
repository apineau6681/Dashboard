import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

# Your FRED API key
fred_api_key = os.getenv("FRED_API_KEY")

# Define the FRED API URLs
debt_url = f"https://api.stlouisfed.org/fred/series/observations?series_id=GFDEBTN&api_key={fred_api_key}&file_type=json"
gdp_url = f"https://api.stlouisfed.org/fred/series/observations?series_id=GDP&api_key={fred_api_key}&file_type=json"

# Define parameters to get data from January 1, 2020 to the current date
start_date = '2020-01-01'
end_date = datetime.now().strftime('%Y-%m-%d')

params = {
    'format': 'json',
    'frequency': 'q',  # Quarterly frequency for GDP
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

# Get debt and GDP data
debt_data = get_data(debt_url, params)
gdp_data = get_data(gdp_url, params)

# Function to ensure data has 'date' and 'value' columns
def ensure_columns(data, label):
    if 'date' not in data.columns or 'value' not in data.columns:
        print(f"Data for {label} does not contain required columns. Columns present: {data.columns.tolist()}")
        raise ValueError(f"Expected columns 'date' and 'value' are missing in the {label} data.")

# Ensure both datasets have the required columns
for data, label in [(debt_data, 'Debt'), (gdp_data, 'GDP')]:
    ensure_columns(data, label)

# Convert 'date' to datetime format and 'value' to numeric
def convert_data(data):
    data['date'] = pd.to_datetime(data['date'])
    data['value'] = pd.to_numeric(data['value'], errors='coerce')
    return data

# Apply conversion
debt_data = convert_data(debt_data)
gdp_data = convert_data(gdp_data)

# Filter and sort data
def filter_and_sort(data):
    data = data[data['date'] >= pd.to_datetime(start_date)]
    return data.sort_values(by='date')

# Apply filtering and sorting
debt_data = filter_and_sort(debt_data)
gdp_data = filter_and_sort(gdp_data)

# Rename columns
debt_data = debt_data.rename(columns={'value': 'Debt'})
gdp_data = gdp_data.rename(columns={'value': 'GDP'})

# Merge the datasets on the Date column
merged_data = pd.merge(debt_data[['date', 'Debt']], gdp_data[['date', 'GDP']], on='date', how='inner')

# Rename the 'date' column to 'Date' and standardize the date format to YYYY-MM-DD
merged_data.rename(columns={'date': 'Date'}, inplace=True)
merged_data['Date'] = merged_data['Date'].dt.strftime('%Y-%m-%d')

# Set up Google Sheets connection
current_dir = os.path.dirname(os.path.abspath(__file__))
service_account_file = os.path.join(current_dir, 'dashboardcrypto-431910-f1f9c1cf4069.json')
spreadsheet_id = '1tgkiZzKp4m9sBOhjvj_3nvlvYJ4N8W9INGn7wFh8a4o'
range_name = 'Sheet2'

# Set up Google Sheets API client
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_file, scope)
client = gspread.authorize(creds)

# Open the Google Sheet
spreadsheet = client.open_by_key(spreadsheet_id)
sheet = spreadsheet.worksheet(range_name)

# Clear the sheet before writing new data
sheet.clear()

# Print column names to verify
print("Merged data columns:", merged_data.columns.tolist())

# Set the headers
sheet.append_row(merged_data.columns.tolist())

# Write the data to the sheet
for row in merged_data.values.tolist():
    sheet.append_row(row)
