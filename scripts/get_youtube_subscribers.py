import pandas as pd
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import datetime
import logging
import os

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the log file path
log_file_path = os.path.join(current_dir, '../log/youtube_api_log.txt')

# Logging configuration
logging.basicConfig(
    filename=log_file_path,  # Nom du fichier de log
    level=logging.INFO,              # Niveau de log
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format du log
)

# Function to get the channel ID from the identifier or URL
def get_channel_id(api_key, identifier):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        if identifier.startswith('@'):
            request = youtube.search().list(
                part='snippet',
                q=identifier,
                type='channel'
            )
            response = request.execute()
            if 'items' in response and response['items']:
                #logging.info(f"Channel ID found for {identifier}: {channel_id}")
                return response['items'][0]['snippet']['channelId']
        else:
            logging.info(f"identifier provided is channel ID {identifier}")
            return identifier
        return None
    except Exception as e:
        logging.error(f"Error when retrieving ID of channel {identifier}: {e}")

# Function to get the number of subscribers
def get_subscriber_count(api_key, channel_id):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.channels().list(
            part='statistics',
            id=channel_id
        )
        response = request.execute()
        if 'items' in response and response['items']:
            subscriber_count = response['items'][0]['statistics']['subscriberCount']
            logging.info(f"number of subscribers returned fo {channel_id}: {subscriber_count}")
            return int(subscriber_count)
        else:
            logging.warning(f"No stat found for channel {channel_id}")
            return None
    except Exception as e:
        logging.error(f"Error returned when retrieving number of subscribers for channel {channel_id}: {e}")

# Function to get the total view count
def get_view_count(api_key, channel_id):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.channels().list(
            part='statistics',
            id=channel_id
        )
        response = request.execute()
        if 'items' in response and response['items']:
            view_count = response['items'][0]['statistics']['viewCount']
            logging.info(f"number of views returned for {channel_id}: {view_count}")
            return int(view_count)
        else:
            logging.warning(f"No stat found for channel {channel_id}")
            return None
    except Exception as e:
        logging.error(f"Error when retrieving view count for channel {channel_id}: {e}")

# Function to append data to Google Sheets
def append_to_google_sheet_subscribers(df, service_account_file, spreadsheet_id, range_name):
    try:
        creds = Credentials.from_service_account_file(service_account_file)
        service = build('sheets', 'v4', credentials=creds)
        
        # Prepare column headers
        column_ids = df['column_id'].tolist()
        subscribers = df['subscribers'].tolist()
        #print(subscribers)
         # Add 'Date' column if it doesn't exist
        if 'Date' not in column_ids:
            column_ids.insert(0, 'Date')  # Ajouter 'Date' au début des en-têtes

        # Add the current date to each data row
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')  # Format de la date : YYYY-MM-DD
        subscribers_with_date = [current_date] + subscribers  # Add date in first position
    
        # Prepare values to be sent to Google Sheets
        values = [subscribers_with_date]  # one line with subscribers
        body = {
            'values': values
        }
        
        # Add headers if they don't exist
        sheet = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        existing_values = sheet.get('values', [])

        # Add headers if they don't exist
        if not existing_values:
            header = [column_ids]
            body['values'].insert(0, header)
        
        # Append the new row to the end of the existing data
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        #print(f"Appended {result.get('updates', {}).get('updatedCells', 0)} cells in {range_name}")
        logging.info(f"Appended {result.get('updates', {}).get('updatedCells', 0)} cells in {range_name}")
    except Exception as e:
        logging.error(f"Error when adding data to the Google Sheets: {e}")

# Function to append data to Google Sheets
def append_to_google_sheet_views(df, service_account_file, spreadsheet_id, range_name):
    try:
        creds = Credentials.from_service_account_file(service_account_file)
        service = build('sheets', 'v4', credentials=creds)
        
        # Prepare column headers
        column_ids = df['column_id'].tolist()
        views = df['views'].tolist()
        #print(views)
         # Add 'Date' column if it doesn't exist
        if 'Date' not in column_ids:
            column_ids.insert(0, 'Date')  # Ajouter 'Date' au début des en-têtes

        # Add the current date to each data row
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')  # Format de la date : YYYY-MM-DD
        views_with_date = [current_date] + views  # Add date in first position
    
        # Prepare values to be sent to Google Sheets
        values = [views_with_date]  # one line with subscribers
        body = {
            'values': values
        }
        
        # Add headers if they don't exist
        sheet = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        existing_values = sheet.get('values', [])

        # Add headers if they don't exist
        if not existing_values:
            header = [column_ids]
            body['values'].insert(0, header)
        
        # Append the new row to the end of the existing data
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        #print(f"Appended {result.get('updates', {}).get('updatedCells', 0)} cells in {range_name}")
        logging.info(f"Appended {result.get('updates', {}).get('updatedCells', 0)} cells in {range_name}")
    except Exception as e:
        logging.error(f"Error when adding data to the Google Sheets: {e}")

# Main function to fetch data and append it to Google Sheets
def fetch_and_append(api_key, csv_file, service_account_file, spreadsheet_id, range_name):
    try:
        df = pd.read_csv(csv_file, sep=';')
        #df = pd.read_csv('channels_test.csv', sep=';')
        
         # Ensure 'url_or_id' column is present
        if 'url_or_id' not in df.columns:
            raise KeyError("The CSV file must contain a 'url_or_id' column.")
        
        logging.info("Retrieving channel IDs")
        # Get channel IDs, subscribers, and views
        df['channel_id'] = df['url_or_id'].apply(lambda x: get_channel_id(api_key, x))
        df['subscribers'] = df['channel_id'].apply(lambda x: get_subscriber_count(api_key, x) if x else None)
        df['views'] = df['channel_id'].apply(lambda x: get_view_count(api_key, x) if x else None)

         # Create 'column_id' without '@' if necessary
        df['column_id'] = df['url_or_id'].apply(lambda x: x[1:] if x.startswith('@') else x)
        
        logging.info("Adding data in Google Sheets")
        # Append data to Google Sheets
        #append_to_google_sheet_subscribers(df, service_account_file, spreadsheet_id, 'Sheet1')
        append_to_google_sheet_views(df, service_account_file, spreadsheet_id, 'Sheet2')
    except Exception as e:
        logging.error(f"Error when retrieving and adding data: {e}")

# Main function
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the log file path
    csv_file = os.path.join(current_dir, 'channels.csv')
    # Youtube API key and service account json to access google sheets
    api_key = os.getenv("YOUTUBE_API_KEY")
    service_account_file = os.path.join(current_dir, 'dashboardcrypto-431910-f1f9c1cf4069.json')
    spreadsheet_id = '1KxY1rkhY8YE6BArS69qu4e1LeutR-fvQk26mxU3lrL0'
    range_name = 'Sheet1'  # Sheet range we want to add the data

    logging.info("Script start")
    # Main function call
    fetch_and_append(api_key, csv_file, service_account_file, spreadsheet_id, range_name)
    logging.info("End of script")