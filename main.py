"""
ETL pipeline for Iowa liquor sales and census data.

Extracts data from BigQuery public datasets and Iowa Data Portal,
cleans and joins the datasets, and creates output tables for analysis.
"""

import os
from google.cloud import bigquery
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_PUBLIC_DATASET = "bigquery-public-data"
BQ_PUBLIC_TABLE = "iowa_liquor_sales.sales"
IOWA_CENSUS_URL = "https://data.iowa.gov/api/dataset-download?path=datasets%2F707%2Frows.json"

def get_bigquery_client():
    """
    Initialize BigQuery client.

    Returns:
        bigquery.Client: Authenticated BigQuery client for the configured GCP project.
    """
    return bigquery.Client(project=GCP_PROJECT_ID)

def extract_liquor_sales(client):
    """
    Extract Iowa Liquor Sales data from BigQuery.

    Args:
        client (bigquery.Client): BigQuery client for querying.

    Returns:
        pd.DataFrame: Iowa liquor sales data from the last 3 years.
    """
    query = """ SELECT * FROM `bigquery-public-data.iowa_liquor_sales.sales` WHERE EXTRACT(YEAR FROM date) > (EXTRACT(YEAR FROM CURRENT_DATE())-3)"""
    query_job = client.query(query)
    df = query_job.to_dataframe()

    return df

def extract_census_data():
    """
    Extract Iowa Census population data from Iowa Data Portal.

    Returns:
        pd.DataFrame: Iowa census population data by county.
    """
    response = requests.get(IOWA_CENSUS_URL)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)

    return df

def clean_and_join_data(liquor_df, census_df):
    """
    Clean and join liquor sales and census datasets.

    Args:
        liquor_df (pd.DataFrame): Raw liquor sales data.
        census_df (pd.DataFrame): Raw census population data.

    Returns:
        pd.DataFrame: Cleaned and joined dataset ready for analysis.
    """
    pass

def create_output_tables(joined_df):
    """
    Create three output tables from processed data.

    Generates analysis tables for insights on liquor sales by county,
    sales trends over time, and population-adjusted metrics.

    Args:
        joined_df (pd.DataFrame): Processed and joined dataset.
    """
    pass

if __name__ == "__main__":
    if not GCP_PROJECT_ID:
        raise ValueError("GCP_PROJECT_ID not set in .env file")

    try:
        client = get_bigquery_client()
        print(f"✓ BigQuery client initialized")
        print(f"✓ Project ID: {GCP_PROJECT_ID}")
        
        print(f"✓ Extracting Iowa Liquor Sales data from BigQuery...")
        liquor_df = extract_liquor_sales(client)
        print(f"✓ Extracted {len(liquor_df)} rows of liquor sales data")

        print(f"✓ Extracting Iowa Census data from Data Portal...")
        census_df = extract_census_data()
        print(f"✓ Extracted {len(census_df)} rows of census data")
    except Exception as e:
        print(f"✗ Error: {e}")
        print("Ensure GOOGLE_APPLICATION_CREDENTIALS is set correctly")
