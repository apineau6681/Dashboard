import tweepy
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Twitter API credentials
API_KEY = 'XtWKJhDjWqeek1jfwrPmP6lzk'
API_SECRET = 'DkOsw364Eyt9S97IHXGmuzhdHBp6o9C202SpKV4OJd5r4KLFsh'
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAABExvQEAAAAAoclNPuhL2Z9Nj6X44SjQBjAktxk%3DcG5yqHuEKNTeWYsmxm0l4FQZpwgr2WE26KcORP5D44FgHPbeJb'

# Authenticate to the Twitter API
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# List of Twitter usernames to check
usernames = ['jack', 'elonmusk', 'twitter']

# Get the current date
current_date = datetime.now().strftime('%Y-%m-%d')

# Create a dictionary to hold the data
data = {'Date': current_date}

# Fetch follower count for each username and add to dictionary
for username in usernames:
    user = client.get_user(username=username)
    followers_count = user.data['public_metrics']['followers_count']
    data[username] = followers_count

# Create a pandas DataFrame with a single row
df = pd.DataFrame([data])

print(df)

# Save the DataFrame to a Google Sheet

# Google Sheets API credentials
SERVICE_ACCOUNT_FILE = 'dashboardcrypto-431910-f1f9c1cf4069.json'
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Authenticate with Google Sheets
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# Open the Google Sheet (replace with your own sheet ID)
#SPREADSHEET_ID = 'your_spreadsheet_id'
#sheet = client.open_by_key(SPREADSHEET_ID)

# Select the first sheet in the spreadsheet
#worksheet = sheet.get_worksheet(0)

# Append data to the Google Sheet
#worksheet.append_row(df.iloc[0].tolist(), value_input_option="RAW")

print("Data saved to Google Sheet successfully!")
