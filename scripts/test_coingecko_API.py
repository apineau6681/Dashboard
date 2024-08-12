import requests

#url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1"
url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=usd&from=2024-08-09&to=2024-08-11"
response = requests.get(url)

if response.status_code == 200:
    print("Success:", response.json())
else:
    print(f"Error: HTTP Status Code: {response.status_code}")
