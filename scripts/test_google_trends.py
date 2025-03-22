from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime, timedelta
import os
import gspread
from google.oauth2 import service_account

# Google Sheets authentication setup
SERVICE_ACCOUNT_FILE = 'dashboardcrypto-431910-f1f9c1cf4069.json'  # Path to your service account credentials JSON file
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, SERVICE_ACCOUNT_FILE)
creds = service_account.Credentials.from_service_account_file(script_path, scopes=SCOPES)
client = gspread.authorize(creds)

# Define the Google Sheet ID and the worksheet name
SPREADSHEET_ID = '1NcBARP6HAUQYepIvXWLciVmxZ-FKRq16k0HgXwlyn2o'
WORKSHEET_NAME = 'test_trends'  # Name of the worksheet where you want to write the data

def save_to_google_sheets(data, spreadsheet_id, worksheet_name):
    # Open the spreadsheet and select the worksheet
    worksheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)
    
    # Clear the existing content in the sheet
    worksheet.clear()

    # Add the header row
    header = ['Date', 'Trend', 'isPartial']
    worksheet.append_row(header)

    # Convert the Timestamp to string
    data['date'] = data.index.strftime('%Y-%m-%d')

    # Convert dataframe to list of lists (rows)
    data_list = data[['date', 'bitcoin', 'isPartial']].values.tolist()

    # Append the data to Google Sheets
    worksheet.append_rows(data_list)

def test_google_trends(nb_days=30):
    # Calculer la date de début en fonction du nombre de jours (nb_days)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=nb_days)
    
    # Convertir les dates en format "YYYY-MM-DD"
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Initialisation de pytrends
    pytrends = TrendReq(hl='en-US', tz=360)

    # Paramètres pour Google Trends
    keywords = ['bitcoin']
    pytrends.build_payload(keywords, cat=0, timeframe=f'{start_date_str} {end_date_str}', geo='', gprop='')

    # Obtenir les données de Google Trends
    trends_df = pytrends.interest_over_time()

    # Vérifier si des données ont été récupérées
    if trends_df.empty:
        print(f"Aucune donnée Google Trends récupérée pour la période {start_date_str} - {end_date_str}.")
    else:
        # Si des données sont récupérées, loggez-les
        print(f"Données Google Trends récupérées pour la période {start_date_str} - {end_date_str}:")
        print(trends_df.head())  # Afficher les premières lignes pour vérifier

        # Sauvegarder les données dans Google Sheets
        save_to_google_sheets(trends_df, SPREADSHEET_ID, WORKSHEET_NAME)

        # Optionnel: Enregistrer les données dans un fichier CSV pour vérifier
        trends_df.to_csv('google_trends_data.csv', index=False)

# Exécuter la fonction de test avec le nombre de jours souhaité
test_google_trends(nb_days=30)  # Exemple : 30 derniers jours
