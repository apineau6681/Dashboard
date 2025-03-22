from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import os

# Initialize the Google Ads client
current_dir = os.path.dirname(os.path.abspath(__file__))
google_ads_file = os.path.join(current_dir, 'google_ads.yaml')
client = GoogleAdsClient.load_from_storage(google_ads_file)

def get_test_ad_data(client, customer_id):
    ga_service = client.get_service("GoogleAdsService")

    # Example GAQL query for test data
    query = """
        SELECT
            ad_group_ad.ad.id,
            ad_group_ad.ad.text_ad.headline,
            metrics.average_cpc,
            metrics.average_cpm
        FROM ad_group_ad
        WHERE
            ad_group_ad.ad.text_ad.headline LIKE '%test%'
        """

    # Execute the query
    response = ga_service.search(customer_id=customer_id, query=query)

    # Iterate over the results and print them
    for row in response:
        print(f"Ad ID: {row.ad_group_ad.ad.id}")
        print(f"Headline: {row.ad_group_ad.ad.text_ad.headline}")
        print(f"Average CPC: {row.metrics.average_cpc.micros / 1_000_000} USD")
        print(f"Average CPM: {row.metrics.average_cpm.micros / 1_000_000} USD")
        print("-------------------------------")

try:
    customer_id = 'YOUR_TEST_ACCOUNT_ID'  # Replace with your test account ID
    get_test_ad_data(client, customer_id)
except GoogleAdsException as ex:
    print(f"Request failed with status '{ex.error.code().name}', and includes the following errors:")
    for error in ex.failure.errors:
        print(f"\t{error.message}")
