import requests
import pandas as pd
import numpy as np
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

# Define the start and end dates
start_date = '2012-11-28'
end_date = pd.Timestamp.now().strftime('%Y-%m-%d')

# Convert the dates to UNIX timestamps (required by CoinGecko API)
start_timestamp = int(pd.Timestamp(start_date).timestamp())
end_timestamp = int(pd.Timestamp(end_date).timestamp())

# Fetch historical data for BTC from CoinGecko API
url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=usd&from={start_timestamp}&to={end_timestamp}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    if 'prices' in data:
        prices = data['prices']
        btc_data = pd.DataFrame(prices, columns=['Date', 'Close'])
        
        # Convert the timestamp to a readable date format
        btc_data['Date'] = pd.to_datetime(btc_data['Date'], unit='ms')
        
        # Calculate the log of the Close price
        btc_data['Log_Close'] = np.log(btc_data['Close'])
        
        # Add additional columns for Open, High, and Low (as Close)
        btc_data['Open'] = btc_data['Close']
        btc_data['High'] = btc_data['Close']
        btc_data['Low'] = btc_data['Close']
        
        # Select the desired columns
        selected_columns = btc_data[['Date', 'Open', 'High', 'Low', 'Close', 'Log_Close']]
        
        # Convert dates to string format for Google Sheets
        selected_columns['Date'] = selected_columns['Date'].astype(str)

        # Authentication with Google Sheets
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = 'dashboardcrypto-431910-f1f9c1cf4069.json'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, SERVICE_ACCOUNT_FILE)
        creds = service_account.Credentials.from_service_account_file(script_path, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)

        # ID de la feuille Google où vous voulez écrire les données
        SPREADSHEET_ID = '1ZAmr2whnm-OFGGRxQJktOUKaouNyYknHIHWbGOKvEbA'
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
        
    else:
        print("Error: 'prices' not found in the API response. The response received was:", data)
else:
    print(f"Error: Failed to fetch data from CoinGecko API. HTTP Status Code: {response.status_code}")

# Optional: Save the data to a CSV file
#csv_filename = 'btc_data_from_2012_with_dates.csv'
#selected_columns.to_csv(csv_filename, index=False, header=True)
#print(f"The data has been saved to {csv_filename}")
