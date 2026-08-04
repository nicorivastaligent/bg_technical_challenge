import utils.gold as gold
from dotenv import load_dotenv
import os 
from google.cloud import bigquery

load_dotenv()
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
LIQUOR_TABLE = f"{GCP_PROJECT_ID}.dev_taligent_bg_technicall_challenge_iowa_silver.liquor_sales_data"
CENSUS_TABLE = f"{GCP_PROJECT_ID}.dev_taligent_bg_technicall_challenge_iowa_silver.census_data"
if __name__ == "__main__":
    if not GCP_PROJECT_ID:
        raise ValueError("GCP_PROJECT_ID not set in .env file")
    
    try:
        client = bigquery.Client(project=GCP_PROJECT_ID)
        print(f"✓ BigQuery client initialized")
        gold.create_country_sales_summary_df(client, LIQUOR_TABLE, CENSUS_TABLE)
        gold.create_store_and_product_analysis_df(client, LIQUOR_TABLE)
        gold.create_price_inflation_tracker_df(client, LIQUOR_TABLE)
        
    except Exception as e:
        print(f"Error: {e}")