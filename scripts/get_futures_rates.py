import os
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

# Authentication with Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'dashboardcrypto-431910-f1f9c1cf4069.json'

# Get the absolute path of the service account file
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, SERVICE_ACCOUNT_FILE)

# Authenticate and build the service
creds = service_account.Credentials.from_service_account_file(script_path, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

# ID of the Google Sheet where you want to write the data
SPREADSHEET_ID = '1NlSoPqN4v6uqXxFL-8C1Uk-UF3OqhYRCqk1BRubOgL4'
RANGE_NAME = 'Sheet1'

# Define the API endpoint and parameters
url = "https://fapi.binance.com/fapi/v1/fundingRate"
params = {
    "symbol": "BTCUSDT"
}

# Make the API request
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()

    # Prepare the data to be written to the Google Sheet
    values = [["Symbol", "Funding Rate", "Funding Time"]]  # Header row

    for entry in data:
        symbol = entry["symbol"]
        funding_rate = float(entry["fundingRate"])  # Convert to float
        funding_time = datetime.fromtimestamp(entry["fundingTime"] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        values.append([symbol, funding_rate, funding_time])

    # Prepare the request body
    body = {
        'values': values
    }

    # Use the Sheets API to write the data
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="RAW",
        body=body
    ).execute()

    print(f"{result.get('updatedCells')} cells updated in the Google Sheet.")
    
else:
    print(f"Failed to retrieve data: {response.status_code}")
