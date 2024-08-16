import os
import requests
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'dashboardcrypto-431910-f1f9c1cf4069.json'

# Get the absolute path of the service account file
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, SERVICE_ACCOUNT_FILE)

# Authenticate and build the service
creds = service_account.Credentials.from_service_account_file(script_path, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

# Google Sheets ID and range
SPREADSHEET_ID = '1c4oxygENemfqHOIDdTEZeCeZd2UaNwZg7oReAyyeI7k'
RANGE_NAME = 'Sheet1'

def get_google_play_downloads(app_id):
    url = f"https://play.google.com/store/apps/details?id={app_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the div that contains the download count
    download_section = soup.find_all('div', class_='wVqUob')
    for section in download_section:
        download_count_div = section.find('div', class_='ClM7O')
        if download_count_div and 'Downloads' in section.find('div', class_='g1rdde').text:
            download_count = download_count_div.text.strip()
            return convert_download_count(download_count)
    
    return "Download count not found"

def convert_download_count(download_str):
    """Convert human-readable download counts to integer."""
    download_str = download_str.replace(',', '').strip()
    if 'M' in download_str:
        try:
            return int(float(download_str.replace('M', '').replace('+', '').strip()) * 1_000_000)
        except ValueError:
            return "Error converting 'M' value"
    elif 'K' in download_str:
        try:
            return int(float(download_str.replace('K', '').replace('+', '').strip()) * 1_000)
        except ValueError:
            return "Error converting 'K' value"
    elif '+' in download_str:
        try:
            return int(download_str.replace('+', '').strip())
        except ValueError:
            return "Error converting '+' value"
    else:
        try:
            return int(download_str)
        except ValueError:
            return "Error converting value"

def update_google_sheet(data):
    sheet = service.spreadsheets()

    # Fetch existing data from the sheet
    existing_data = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = existing_data.get('values', [])
    
    # Check if the header row is present, otherwise create one
    if not values:
        header = ["Date"] + [app_name for app_name in data.keys()]
        values.append(header)
    
    # Prepare the new row of data
    new_row = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] + [data[app_name] for app_name in data.keys()]
    values.append(new_row)

    body = {
        'values': values
    }

    # Update the sheet
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="RAW",
        body=body
    ).execute()

    print(f"Updated {result.get('updatedCells')} cells.")

def main():
    # App IDs for the mentioned apps
    apps = {
        'Coinbase': 'com.coinbase.android',
        'Binance': 'com.binance.dev',
        'Kraken': 'com.kraken.invest.app',
        'Gemini': 'com.google.android.apps.bard',
        'eToro': 'com.etoro.openbook',
        'Crypto.com': 'co.mona.android',
        'Trust Wallet': 'com.wallet.crypto.trustapp',
        'MetaMask': 'io.metamask',
        'Ledger Live': 'com.ledger.live',
        'CoinGecko': 'com.coingecko.coingeckoapp',
        'Bybit': 'com.bybit.app',
        'KuCoin': 'com.kubi.kucoin'
    }
    
    # Fetch and prepare data
    data = {}
    for app_name, app_id in apps.items():
        downloads = get_google_play_downloads(app_id)
        data[app_name] = downloads
        print(f"Logged {app_name}: {downloads}")
    
    # Update Google Sheets
    update_google_sheet(data)

if __name__ == "__main__":
    main()
