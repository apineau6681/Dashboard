import requests
import datetime

# Remplacez 'your_api_key' par votre clé API CoinMarketCap
api_key = '27ef9274-0003-4b33-8f89-181a5f27f265'
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical'

# En-têtes pour l'autorisation
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': api_key,
}

# Récupérer les données pour les 7 derniers jours
end_date = datetime.datetime.utcnow()
start_date = end_date - datetime.timedelta(days=7)

params = {
    'symbol': 'BTC',
    'time_start': int(start_date.timestamp()),
    'time_end': int(end_date.timestamp()),
    'interval': 'daily',
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    quotes = data['data']['quotes']
    
    for quote in quotes:
        time_close = quote['time_close']
        average_price = (quote['quote']['USD']['high'] + quote['quote']['USD']['low']) / 2
        print(f"Date: {time_close}, Prix moyen: {average_price}")
else:
    print(f"Erreur {response.status_code}: {response.json()}")