import yfinance as yf
import logging
from datetime import datetime, timedelta

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Fonction pour récupérer le prix de clôture du BTC de la veille
def get_bitcoin_price():
    try:
        # Déterminer la date de la veille
        yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Récupérer les données du Bitcoin
        btc = yf.Ticker("BTC-USD")
        hist = btc.history(period="5d")  # Récupère les 5 derniers jours pour assurer la dispo de la veille
        
        # Vérifier que les données sont bien récupérées
        if hist.empty:
            logging.error("Aucune donnée récupérée pour BTC-USD.")
            return None
        
        # Récupérer la date et le prix de clôture de la veille
        closing_price = hist['Close'].iloc[-2]  # Avant-dernier jour
        closing_date = hist.index[-2].strftime('%Y-%m-%d')

        # Vérification que la date correspond bien à hier
        if closing_date != yesterday:
            logging.warning(f"La date récupérée ({closing_date}) ne correspond pas à hier ({yesterday}).")
        
        logging.info(f"Prix de clôture du Bitcoin pour {closing_date}: {closing_price}")
        return closing_price
    except Exception as e:
        logging.error(f"Erreur lors de la récupération du prix du Bitcoin : {e}")
        return None

# Exécution du test
if __name__ == "__main__":
    btc_price = get_bitcoin_price()
    if btc_price is not None:
        print(f"Test réussi : Prix de clôture du Bitcoin récupéré = {btc_price}")
    else:
        print("Test échoué : Impossible de récupérer le prix de clôture du Bitcoin.")
