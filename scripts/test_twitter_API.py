import tweepy
import os
import pandas as pd

# Twitter API credentials (use environment variables or replace with actual values for testing)
#API_KEY = os.getenv('TWITTER_API_KEY', 'lxtlBsr7zveCeOVSyCVqe19Bh')
#API_SECRET = os.getenv('TWITTER_API_SECRET', 'MazZ1B496UJXmSWGY2zYqPK2W9K1BHuuqRQH8oqfLDHdR9ZlS1')
#BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', 'AAAAAAAAAAAAAAAAAAAAABExvQEAAAAAoclNPuhL2Z9Nj6X44SjQBjAktxk%3DcG5yqHuEKNTeWYsmxm0l4FQZpwgr2WE26KcORP5D44FgHPbeJb')
#ACCESS_TOKEN = 

bearer_token = 'AAAAAAAAAAAAAAAAAAAAABExvQEAAAAANRuHUdwjA0gpVa4Topp3dv40f%2BI%3D9aJ1KNUaX8vY719it5XWnlONRsj5Q05x1KeRiJ9ObsOQgn3VnP'
access_token = '1373551084489297920-sEahbYsIVqxA8a2AmGjqIE7tyklzam'
access_token_secret = 'gsKH9AEijCtDiLGp8Y8BwHSd5L820ohzpmoLqRXEuSgWe'

# Authenticate to the Twitter API using the Bearer Token
def getClient():
    client = tweepy.Client(bearer_token='AAAAAAAAAAAAAAAAAAAAABExvQEAAAAANRuHUdwjA0gpVa4Topp3dv40f%2BI%3D9aJ1KNUaX8vY719it5XWnlONRsj5Q05x1KeRiJ9ObsOQgn3VnP')
    print("Twitter API Authentication successful!")
    return client

def getUserInfo(client,username):
    user = client.get_user(username=username,user_fields='public_metrics')
    return user

try:
    client = getClient()
    # Authenticate to the Twitter API using the Bearer Token
    d =getUserInfo(client,'ElonMusk')
    d.data.public_metrics['followers_count']
    print(d)
except Exception as e:
    print(f"Error fetching user data: {e}")

