import utils.silver as silver 
from dotenv import load_dotenv
import os
import pandas as pd
from google.cloud import bigquery

load_dotenv()
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BQ_PUBLIC_DATASET = "bigquery-public-data"
BQ_PUBLIC_TABLE = "iowa_liquor_sales.sales"

def main(request):
    """
        Cloud Function to clean and transform Iowa census population data and liquor sales data, and upload them to BigQuery.
        Args:
            request (flask.Request): The request object.
        Returns:
            Code 200 if successful, Code 500 if an error occurs.
    """
    if not GCP_PROJECT_ID:
        raise ValueError("GCP_PROJECT_ID not set in .env file")
    
    try:
        client = bigquery.Client(project=GCP_PROJECT_ID)
        print(f"✓ BigQuery client initialized")

        gcs_path = "gs://dev-taligent-bg-technicall-challenge-gcs-bronze/bronze/census/iowa_census.parquet"
        census_df = pd.read_parquet(gcs_path)
        print(f"✓ Extracted {len(census_df)} rows of census data")

        census_df = silver.clean_census_data(census_df)
        silver.upload_to_bigquery(census_df, 'census_data', client, GCP_PROJECT_ID)

        silver.incremental_load_to_bigquery_liquor(client, GCP_PROJECT_ID)

        return "Data transformation completed successfully", 200
    except Exception as e:
        print(f"Error: {e}")
        return f"Internal Error: {e}", 500