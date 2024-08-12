import requests
import pandas as pd

# URL de l'API CryptoCompare pour récupérer les prix historiques journaliers de BTC en USD
url = "https://min-api.cryptocompare.com/data/v2/histoday"

# Paramètres de la requête
params = {
    "fsym": "BTC",    # Symbole de la crypto (BTC)
    "tsym": "USD",    # Symbole de la devise (USD)
    "limit": 10       # Nombre de jours de données à récupérer (max 2000)
}

# Envoyer la requête à l'API
response = requests.get(url, params=params)

# Vérifier si la requête a été réussie
if response.status_code == 200:
    print("Connexion réussie à l'API CryptoCompare!")
    data = response.json()
    
    # Extraire les données et les convertir en DataFrame
    if 'Data' in data and 'Data' in data['Data']:
        btc_data = pd.DataFrame(data['Data']['Data'])
        
        # Convertir les timestamps en dates lisibles
        btc_data['time'] = pd.to_datetime(btc_data['time'], unit='s')
        
        # Afficher les premières lignes du DataFrame
        print(btc_data.head())
    else:
        print("Erreur: Les données ne sont pas disponibles dans la réponse.")
else:
    print(f"Erreur: Impossible de se connecter à l'API. Code de statut HTTP: {response.status_code}")
