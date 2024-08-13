import pandas as pd
import gspread
import os
from google.oauth2 import service_account
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from google.oauth2.service_account import Credentials

# Google Sheets API credentials and setup
SERVICE_ACCOUNT_FILE = 'dashboardcrypto-431910-f1f9c1cf4069.json'  # Path to your service account credentials JSON file
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, SERVICE_ACCOUNT_FILE)
creds = service_account.Credentials.from_service_account_file(script_path, scopes=SCOPES)
client = gspread.authorize(creds)

# Define the Google Sheet ID and the worksheet name
SPREADSHEET_ID = '1sF83Zm6rUP-T3eVVEOpY2WJKaaNUTXZUW_bBc0iVkwY'
WORKSHEET_NAME = 'Sheet1'  # Name of the worksheet where you want to write the data

OUTPUT_SPREADSHEET_ID = '1yhCjXZ7gHJyRI6So9y9x6njyioIn8iHLhK3tZQ9xUno'
OUTPUT_WORKSHEET_NAME = 'Sheet1'  # Name of the worksheet where you want to write the results

# Access the Google Sheet and read the input data
spreadsheet = client.open_by_key(SPREADSHEET_ID)
input_worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
btc_data = get_as_dataframe(input_worksheet, header=0)

# Specify the path to the CSV file
#csv_file_path = 'btc_data_from_2012_with_dates.csv'
# Load the CSV file into a DataFrame
#btc_data = pd.read_csv(csv_file_path)

#NB of days to be returned
nb_days = 600

#From_2012_11_28 = '2012-11-28'
From_2016_07_09 = '2016-07-09'
From_2020_05_11 = '2020-05-11'
From_2024_04_20 = '2024-04-20'

#Declare ROI dataframe
df_roi = pd.DataFrame(index=range(1, nb_days), columns = ['From_2016_07_09', 'From_2020_05_11', 'From_2024_04_20'])  # Index de 1 à 10
# Set the name for the index column
df_roi.index.name = 'Day'

roi_start_dates = {
    'From_2016_07_09': From_2016_07_09,
    'From_2020_05_11': From_2020_05_11,
    'From_2024_04_20': From_2024_04_20
}



for period, start_date in roi_start_dates.items():
  #set price day1
  initial_price = btc_data.loc[btc_data['Date'] == start_date, 'Close'].values[0]

  #calculates ROI for the next nb_days
  for day in range(1, nb_days+1):
    day_date = pd.to_datetime(start_date) + pd.Timedelta(days=day)
    day_date_str = day_date.strftime('%Y-%m-%d')

    #retrieve BTC price at the given date
    btc_day_price = btc_data.loc[btc_data['Date'] == day_date_str,'Close']

    # Check if there is a price for the given date
    if not btc_day_price.empty:
      #calcultates ROI of the day
      #roi_day = ((btc_day_price.values[0] - initial_price) / initial_price) * 100
      btc_day_price = btc_day_price.values[0]  # Get the scalar value
      roi_day = btc_day_price / initial_price
      # Assign the ROI value to the 'period' column in roi_df
      #roi_df.loc[day, period] = btc_day_price.values[0].round(2)
      df_roi.loc[day, period] = round(roi_day, 2)
    else:
      df_roi.loc[day, period] = None  # Assigner None si aucune donnée disponible

print(df_roi)

# Access the output Google Sheet and write the DataFrame
output_spreadsheet = client.open_by_key(OUTPUT_SPREADSHEET_ID)
output_worksheet = output_spreadsheet.worksheet(OUTPUT_WORKSHEET_NAME)
set_with_dataframe(output_worksheet, df_roi, include_index=True, include_column_header=True)
print("Data has been successfully read from the input Google Sheet and written to the output Google Sheet.")

######### CSV
# Save dataframe in CSV file
#path = '/content/drive/MyDrive/Dashboard_Crypto/btc_roi_per_day_with_periods.csv'
#path = './btc_roi_per_day_with_periods.csv'
#df_roi.to_csv(path, index_label='Day')