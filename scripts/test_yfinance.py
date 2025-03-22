import yfinance as yf
from datetime import datetime, timedelta
import gspread
from google.oauth2 import service_account
import os
import pandas as pd

# Google Sheets authentication setup
SERVICE_ACCOUNT_FILE = 'dashboardcrypto-431910-f1f9c1cf4069.json'  # Path to your service account credentials JSON file
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, SERVICE_ACCOUNT_FILE)
creds = service_account.Credentials.from_service_account_file(script_path, scopes=SCOPES)
client = gspread.authorize(creds)

# Define the Google Sheet ID and the worksheet name
SPREADSHEET_ID = '1NcBARP6HAUQYepIvXWLciVmxZ-FKRq16k0HgXwlyn2o'
WORKSHEET_NAME = 'test'  # Name of the worksheet where you want to write the data

def save_to_google_sheets(df, spreadsheet_id, tab_name):
    # Ouvrir la feuille de calcul avec l'ID et le nom de l'onglet
    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(tab_name)

    # Convertir les dates (index) en chaînes de caractères au format "YYYY-MM-DD"
    df.index = df.index.strftime('%Y-%m-%d')

    # Convertir le DataFrame en liste de listes (à envoyer dans Google Sheets)
    data = df.reset_index().values.tolist()  # Réinitialiser l'index pour transformer en liste de lignes

    # Ajouter les en-têtes de colonnes à la première ligne
    columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    data.insert(0, columns)

    # Écrire les données dans la feuille
    worksheet.append_rows(data)

def test_btc_data(nb_days=30):
    # Calculer la date de début en fonction du nombre de jours (nb_days)
    end_date = datetime.today() - timedelta(days=1)  # Exclure le jour actuel
    start_date = end_date - timedelta(days=nb_days)

    # Convertir les dates en format "YYYY-MM-DD"
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Télécharger les données de Bitcoin à partir de Yahoo Finance
    btc = yf.download("BTC-USD", start=start_date_str, end=end_date_str)

    # Vérifier si des données ont été récupérées
    if btc.empty:
        print(f"Aucune donnée Bitcoin récupérée pour la période {start_date_str} - {end_date_str}.")
    else:
        # Si des données sont récupérées, loggez-les
        print(f"Données Bitcoin récupérées pour la période {start_date_str} - {end_date_str}:")
        print(btc.head())  # Afficher les premières lignes pour vérifier

        # Afficher toutes les dates disponibles
        print("\nToutes les dates disponibles dans les données récupérées :")
        print(btc.index)

        # Sauvegarder dans Google Sheets
        save_to_google_sheets(btc, SPREADSHEET_ID, WORKSHEET_NAME)

# Exécuter la fonction de test avec le nombre de jours souhaité
test_btc_data(nb_days=30)  # Exemple : 30 derniers jours
