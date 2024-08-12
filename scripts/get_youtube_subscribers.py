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

# Configuration du logging
logging.basicConfig(
    filename=log_file_path,  # Nom du fichier de log
    level=logging.INFO,              # Niveau de log
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format du log
)

# Fonction pour obtenir l'ID de la chaîne à partir de l'identifiant ou de l'URL
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

# Fonction pour obtenir le nombre d'abonnés
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
            return response['items'][0]['statistics']['subscriberCount']
        else:
            logging.warning(f"No stat found for channel {channel_id}")
            return None
    except Exception as e:
        logging.error(f"Error returned when retrieving number of subscribers for channel {channel_id}: {e}")

# Fonction pour ajouter une ligne à Google Sheets
def append_to_google_sheet(df, service_account_file, spreadsheet_id, range_name):
    try:
        creds = Credentials.from_service_account_file(service_account_file)
        service = build('sheets', 'v4', credentials=creds)
        
        # Préparer les en-têtes de colonnes et les abonnés
        column_ids = df['column_id'].tolist()
        subscribers = df['subscribers'].tolist()
        #print(subscribers)
        # Ajouter la colonne 'Date' aux en-têtes si elle n'existe pas
        if 'Date' not in column_ids:
            column_ids.insert(0, 'Date')  # Ajouter 'Date' au début des en-têtes

        # Ajouter la date actuelle à chaque ligne de données
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')  # Format de la date : YYYY-MM-DD
        subscribers_with_date = [current_date] + subscribers  # Ajouter la date en première position
    
        # Préparer les valeurs à envoyer à Google Sheets
        values = [subscribers_with_date]  # Une seule ligne avec les abonnés
        body = {
            'values': values
        }
        
        # Obtenir la plage actuelle des en-têtes
        sheet = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        existing_values = sheet.get('values', [])

        # Ajouter les en-têtes s'ils n'existent pas
        if not existing_values:
            header = [column_ids]
            body['values'].insert(0, header)
        
        # Ajouter la nouvelle ligne à la fin des données existantes
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        #print(f"Appended {result.get('updates', {}).get('updatedCells', 0)} cells in {range_name}")
        logging.info(f"Appended {result.get('updates', {}).get('updatedCells', 0)} cells in {range_name}")
    except Exception as e:
        logging.error(f"Error when adding data to the Google Sheets: {e}")

# Fonction principale pour traiter les données et ajouter à Google Sheets
def fetch_and_append(api_key, csv_file, service_account_file, spreadsheet_id, range_name):
    try:
        df = pd.read_csv(csv_file, sep=';')
        #df = pd.read_csv('channels_test.csv', sep=';')
        
        # Vérifier la présence de la colonne 'url_or_id'
        if 'url_or_id' not in df.columns:
            raise KeyError("The CSV file must contain a 'url_or_id' column.")
        
        logging.info("Retrieving channel IDs")
        # Obtenir les IDs de chaîne et les abonnés
        df['channel_id'] = df['url_or_id'].apply(lambda x: get_channel_id(api_key, x))
        df['subscribers'] = df['channel_id'].apply(lambda x: get_subscriber_count(api_key, x) if x else None)
        
        # Créer la colonne 'column_id' avec le '@' retiré si nécessaire
        df['column_id'] = df['url_or_id'].apply(lambda x: x[1:] if x.startswith('@') else x)
        
        logging.info("Adding data in Google Sheets")
        # Ajouter à Google Sheets avec les données
        append_to_google_sheet(df, service_account_file, spreadsheet_id, range_name)
    except Exception as e:
        logging.error(f"Error when retrieving and adding data: {e}")

# Exemple d'utilisation
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the log file path
    csv_file = os.path.join(current_dir, 'channels.csv')
    # Remplacez par votre clé API YouTube et le chemin vers votre fichier JSON des clés
    api_key = 'AIzaSyDDrOYh5SJHaZw-n99sXFlSMS3uEPLXm4g'
    service_account_file = os.path.join(current_dir, 'dashboardcrypto-431910-f1f9c1cf4069.json')
    spreadsheet_id = '1KxY1rkhY8YE6BArS69qu4e1LeutR-fvQk26mxU3lrL0'
    range_name = 'Sheet1'  # Plage où vous souhaitez ajouter les données, ajustez selon besoin

    logging.info("Démarrage du script")
    # Appel de la fonction principale
    fetch_and_append(api_key, csv_file, service_account_file, spreadsheet_id, range_name)
    logging.info("Fin du script")