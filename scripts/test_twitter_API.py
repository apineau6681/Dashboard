import tweepy
import os
import pandas as pd

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

