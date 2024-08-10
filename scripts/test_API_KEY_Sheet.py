from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Chemin vers le fichier JSON des clés du compte de service
SERVICE_ACCOUNT_FILE = 'dashboardcrypto-431910-f1f9c1cf4069.json'

# Scopes nécessaires pour accéder aux feuilles de calcul
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Créer des credentials à partir du fichier JSON
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Construire le service Google Sheets
service = build('sheets', 'v4', credentials=creds)

# ID de votre feuille de calcul Google Sheets
SPREADSHEET_ID = '1XbTync_phfMbMdQqSXbEQzk6XlgPSi7dumKG3LuK0qA'

# Plage à lire et à écrire
RANGE_NAME = 'Sheet1!A1:B2'

# Exemple de lecture de données
try:
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    print('Data read from sheet:', values)
except Exception as e:
    print('An error occurred while reading data:', e)

# Exemple d'écriture de données
values_to_write = [['Hello', 'World'], ['Test', '123']]
body = {
    'values': values_to_write
}

try:
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption='RAW',
        body=body
    ).execute()
    print(f'{result.get("updatedCells")} cells updated.')
except Exception as e:
    print('An error occurred while writing data:', e)
