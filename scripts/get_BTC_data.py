import yfinance as yf
import pandas as pd
import os
import numpy as np  # Import numpy for log calculations
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Define the start and end dates
start_date = '2012-11-28'
end_date = pd.Timestamp.now().strftime('%Y-%m-%d')

# Download historical data for BTC from Yahoo Finance
btc_data = yf.download('BTC-USD', start=start_date, end=end_date)

# Reset the index to include the date as a column
btc_data.reset_index(inplace=True)

# Add a column for the log price of the Close price
btc_data['Log_Close'] = np.log(btc_data['Close'])

# Convert dates to string format - so it can be JSON serialized
btc_data['Date'] = btc_data['Date'].astype(str)

# Select the desired columns including the date
selected_columns = btc_data[['Date', 'Open', 'High', 'Low', 'Close','Log_Close']]

# Authentification avec Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'dashboardcrypto-431910-f1f9c1cf4069.json'
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, SERVICE_ACCOUNT_FILE)
creds = service_account.Credentials.from_service_account_file(script_path, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

# ID de la feuille Google où vous voulez écrire les données
SPREADSHEET_ID = '1sF83Zm6rUP-T3eVVEOpY2WJKaaNUTXZUW_bBc0iVkwY'
RANGE_NAME = 'Sheet1'

# Convert the DataFrame to a list of lists for Google Sheets
values = [selected_columns.columns.tolist()] + selected_columns.values.tolist()

body = {
    'values': values
}

# Écrire les données dans la feuille Google
result = service.spreadsheets().values().update(
    spreadsheetId=SPREADSHEET_ID,
    range=RANGE_NAME,
    valueInputOption='RAW',
    body=body
).execute()


############## CSV
# Save the data to a CSV file
#csv_filename = 'btc_data_from_2012_with_dates.csv'
#selected_columns.to_csv(csv_filename, index=False, header=True)
#print(f"The data has been saved to {csv_filename}")

