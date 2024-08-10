#get google data

#api_key ='AIzaSyBSVnO4iFd7EKSoEFeJfn44N-bHTbIpJHU'

from googleapiclient.discovery import build

def test_api_key(api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.channels().list(
        part='snippet',
        id='@Bullrunners'  # Example channel ID
    )
    response = request.execute()
    return response

api_key = 'AIzaSyBSVnO4iFd7EKSoEFeJfn44N-bHTbIpJHU'  # Replace with your API key
try:
    response = test_api_key(api_key)
    print("API Key is working. Response:")
    print(response)
except Exception as e:
    print(f"An error occurred: {e}")
