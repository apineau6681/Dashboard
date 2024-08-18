import pandas as pd
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import datetime
import os

# Function to read data from Google Sheets into a DataFrame
def read_from_google_sheet(service_account_file, spreadsheet_id, range_name):
    creds = Credentials.from_service_account_file(service_account_file)
    service = build('sheets', 'v4', credentials=creds)
    
    # Get data from Google Sheet
    sheet = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = sheet.get('values', [])
    
    # Convert to DataFrame
    df = pd.DataFrame(values[1:], columns=values[0])
    
    # Convert Date and Views columns to appropriate types
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df.iloc[:, 1:] = df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
    
    return df

# Function to calculate daily views
def calculate_daily_views(df):
    # Sort by date to ensure proper calculation
    df = df.sort_values(by=['Date'])
    
    # Calculate daily views by subtracting the previous day's views
    df_daily_views = df.copy()
    df_daily_views.iloc[:, 1:] = df.iloc[:, 1:].diff().fillna(0)
    
    # Keep only today's data for appending
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    df_daily_views = df_daily_views[df_daily_views['Date'] == today]
    
    return df_daily_views

# Function to append daily views data to Google Sheets
def append_daily_views_to_google_sheet(df, service_account_file, spreadsheet_id, range_name):
    creds = Credentials.from_service_account_file(service_account_file)
    service = build('sheets', 'v4', credentials=creds)
    
    # Prepare data to be sent to Google Sheets
    values = df.values.tolist()
    body = {
        'values': values
    }
    
    # Append the new rows to the existing data
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    print(f"Appended {result.get('updates', {}).get('updatedCells', 0)} cells in {range_name}")

# Main function to fetch data and calculate daily views
def fetch_and_calculate_daily_views(service_account_file, spreadsheet_id, range_total_views, range_daily_views):
    # Read the existing total views from Google Sheets
    df_total_views = read_from_google_sheet(service_account_file, spreadsheet_id, range_total_views)
    
    # Calculate the daily views
    df_daily_views = calculate_daily_views(df_total_views)
    
    # Append the daily views to the Google Sheet
    append_daily_views_to_google_sheet(df_daily_views, service_account_file, spreadsheet_id, range_daily_views)

# Main function
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    service_account_file = os.path.join(current_dir, 'dashboardcrypto-431910-f1f9c1cf4069.json')
    spreadsheet_id = '1KxY1rkhY8YE6BArS69qu4e1LeutR-fvQk26mxU3lrL0'
    range_total_views = 'views'  # The range where the total views are stored
    range_daily_views = 'daily_views'  # The range where the daily views will be stored

    print("Start calculating daily views")
    
    # Main function call
    fetch_and_calculate_daily_views(service_account_file, spreadsheet_id, range_total_views, range_daily_views)
    
    print("End of daily views calculation script")
