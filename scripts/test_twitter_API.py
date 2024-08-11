import tweepy
import os

# Twitter API credentials (use environment variables or replace with actual values for testing)
API_KEY = os.getenv('TWITTER_API_KEY', 'XtWKJhDjWqeek1jfwrPmP6lzk')
API_SECRET = os.getenv('TWITTER_API_SECRET', 'DkOsw364Eyt9S97IHXGmuzhdHBp6o9C202SpKV4OJd5r4KLFsh')
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', 'AAAAAAAAAAAAAAAAAAAAABExvQEAAAAAoclNPuhL2Z9Nj6X44SjQBjAktxk%3DcG5yqHuEKNTeWYsmxm0l4FQZpwgr2WE26KcORP5D44FgHPbeJb')

# Authenticate to the Twitter API using the Bearer Token
try:
    client = tweepy.Client(bearer_token=BEARER_TOKEN)
    print("Twitter API Authentication successful!")
except Exception as e:
    print(f"Error during Twitter API Authentication: {e}")

# Specify a Twitter username to test the connection
username = 'elonmusk'

# Fetch user data to test API connection
try:
    user = client.get_user(username=username)
    print(f"Successfully retrieved user data for @{username}:")
    print(f"Name: {user.data['name']}")
    print(f"Username: {user.data['username']}")
    print(f"Followers Count: {user.data['public_metrics']['followers_count']}")
except Exception as e:
    print(f"Error fetching user data: {e}")
