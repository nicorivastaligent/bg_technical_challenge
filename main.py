"""
Iowa Liquor Sales & Census Data ETL Pipeline.

Extracts data from BigQuery and Iowa Data Portal, cleans, transforms into 3 analysis tables,
and validates data quality with automated checks.
Requires: GCP_PROJECT_ID environment variable.
"""

import os
from dotenv import load_dotenv
import layer.bronze.utils.bronze as bronze
import layer.silver.silver as silver
import layer.gold.utils.gold as gold
import utils.data_quality as dq

load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_PUBLIC_DATASET = "bigquery-public-data"
BQ_PUBLIC_TABLE = "iowa_liquor_sales.sales"
IOWA_CENSUS_URL = "https://data.iowa.gov/api/dataset-download?path=datasets%2F707%2Frows.json"

if __name__ == "__main__":
    if not GCP_PROJECT_ID:
        raise ValueError("GCP_PROJECT_ID not set in .env file")

    try:
        client = bronze.get_bigquery_client(GCP_PROJECT_ID)
        print(f"✓ BigQuery client initialized")
        print(f"✓ Project ID: {GCP_PROJECT_ID}")
        
        print(f"\n✓ Extracting Iowa Liquor Sales data from BigQuery...")
        liquor_df = bronze.extract_liquor_sales(client)
        dq.validate_table_quality(liquor_df, "Iowa Liquor Sales")
        print(f"✓ Extracted {len(liquor_df)} rows of liquor sales data")

        print(f"\n✓ Extracting Iowa Census data from Data Portal...")
        census_df = bronze.extract_census_data(IOWA_CENSUS_URL)
        dq.validate_table_quality(census_df, "Iowa Census data")
        print(f"✓ Extracted {len(census_df)} rows of census data")

        print(f"\n✓ Cleaning liquor data...")
        liquor_df = silver.clean_liquor_data(liquor_df)
        print(f"✓ Liquor data cleaned")
        
        print(f"\n✓ Cleaning Census data...")
        census_df = silver.clean_census_data(census_df)
        print(f"✓ Census Data cleaned")

        print(f"\n--- TRANSFORMATION ---")
        print(f"✓ Transforming and joining datasets...")
        country_sales_summary_df = gold.create_country_sales_summary_df(liquor_df, census_df)
        print(f"✓ Transformed country_sales_summary_df created with {len(country_sales_summary_df)} rows")
        store_and_product_analysis_df = gold.create_store_and_product_analysis_df(liquor_df)
        print(f"✓ Transformed store_and_product_analysis_df created with {len(store_and_product_analysis_df)} rows")
        price_inflation_tracker_df = gold.create_price_inflation_tracker_df(liquor_df)
        print(f"✓ Transformed price_inflation_tracker_df created with {len(price_inflation_tracker_df)} rows")

        del liquor_df, census_df  # Free memory
            
    except Exception as e:
        print(f"✗ Error: {e}")
