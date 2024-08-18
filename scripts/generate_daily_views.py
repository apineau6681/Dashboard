import pandas as pd
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
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
    df.iloc[:, 1:-1] = df.iloc[:, 1:-1].apply(pd.to_numeric, errors='coerce')  # Apply to all except Date and last column
    
    return df

# Function to calculate daily views for all dates
def calculate_daily_views(df):
    # Sort by date to ensure proper calculation
    df = df.sort_values(by=['Date'])
    
    # Calculate daily views by subtracting the previous day's views
    df_daily_views = df.copy()
    df_daily_views.iloc[:, 1:-1] = df.iloc[:, 1:-1].diff().fillna(0)  # Only calculate diff on view columns
    
    return df_daily_views

# Function to overwrite daily views data in Google Sheets
def overwrite_daily_views_in_google_sheet(df, service_account_file, spreadsheet_id, range_name):
    creds = Credentials.from_service_account_file(service_account_file)
    service = build('sheets', 'v4', credentials=creds)
    
    # Convert Date column to string to avoid serialization issues
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    # Prepare data to be sent to Google Sheets
    values = [df.columns.tolist()] + df.values.tolist()  # Include headers
    body = {
        'values': values
    }
    
    # Clear the existing data in the range
    service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range_name).execute()
    
    # Write the new data to the range
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()

    print(f"Overwritten {result.get('updatedCells', 0)} cells in {range_name}")

# Main function to fetch data, calculate daily views, and overwrite the sheet
def fetch_and_calculate_daily_views(service_account_file, spreadsheet_id, range_total_views, range_daily_views):
    # Read the existing total views from Google Sheets
    df_total_views = read_from_google_sheet(service_account_file, spreadsheet_id, range_total_views)
    
    # Calculate the daily views for all dates
    df_daily_views = calculate_daily_views(df_total_views)
    
    # Overwrite the daily views in the Google Sheet
    overwrite_daily_views_in_google_sheet(df_daily_views, service_account_file, spreadsheet_id, range_daily_views)

# Main function
if __name__ == '__main__':
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        service_account_file = os.path.join(current_dir, 'dashboardcrypto-431910-f1f9c1cf4069.json')
        spreadsheet_id = '1KxY1rkhY8YE6BArS69qu4e1LeutR-fvQk26mxU3lrL0'
        range_total_views = 'views'  # The range where the total views are stored
        range_daily_views = 'daily_views'  # The range where the daily views will be stored

        print("Start calculating and overwriting daily views")
        
        # Main function call
        fetch_and_calculate_daily_views(service_account_file, spreadsheet_id, range_total_views, range_daily_views)
        
        print("End of daily views calculation and overwrite script")
    except Exception as e:
        print(f"An error occurred: {e}")
