import os
from google.cloud import bigquery
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_PUBLIC_DATASET = "bigquery-public-data"
BQ_PUBLIC_TABLE = "iowa_liquor_sales.sales"
IOWA_CENSUS_URL = "https://data.iowa.gov/api/views/707/rows.csv"

def get_bigquery_client():
    """Initialize BigQuery client."""
    return bigquery.Client(project=GCP_PROJECT_ID)

def extract_liquor_sales(client):
    """Extract Iowa Liquor Sales data (last 3 years)."""
    pass

def extract_census_data():
    """Extract Iowa Census population data."""
    pass

def clean_and_join_data(liquor_df, census_df):
    """Clean and join datasets."""
    pass

def create_output_tables(joined_df):
    """Create 3 output tables from processed data."""
    pass

if __name__ == "__main__":
    if not GCP_PROJECT_ID:
        raise ValueError("GCP_PROJECT_ID not set in .env file")

    try:
        client = get_bigquery_client()
        print(f"✓ BigQuery client initialized")
        print(f"✓ Project ID: {GCP_PROJECT_ID}")
        print(f"✓ Setup complete. Ready for ETL pipeline.")
    except Exception as e:
        print(f"✗ Error: {e}")
        print("Ensure GOOGLE_APPLICATION_CREDENTIALS is set correctly")
