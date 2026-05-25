import os
import json

from dotenv import load_dotenv

from google.cloud import bigquery
from google.oauth2 import service_account

load_dotenv()
gcp_key_json = os.getenv("GCP_KEY_JSON")

# Convert string JSON -> dict
gcp_key_dict = json.loads(gcp_key_json)

# Create credentials
credentials = service_account.Credentials.from_service_account_info(
    gcp_key_dict
)

# Create BigQuery client
client = bigquery.Client(
    credentials=credentials,
    project="pipeline-496517"
)

# READ WEATHER FEATURE DATASET

with open("sql/weather_dataset.sql", "r") as file:
    weather_query = file.read()

weather_query_job = client.query(weather_query)

df_weather = weather_query_job.to_dataframe()

print("=== WEATHER FEATURE DATASET ===")
print(df_weather.head())

# READ REGIONAL INSIGHTS

with open("sql/regional_insights.sql", "r") as file:
    insight_query = file.read()

insight_query_job = client.query(insight_query)

df_insights = insight_query_job.to_dataframe()

print("\n=== REGIONAL INSIGHTS ===")
print(df_insights)