import utils.bronze as bronze
from dotenv import load_dotenv
import os 

load_dotenv()
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")
IOWA_CENSUS_URL = "https://data.iowa.gov/api/dataset-download?path=datasets%2F707%2Frows.json"

def main(request):
    """
        Cloud Function to extract Iowa census population data from Iowa Data Portal API and upload it to GCS bucket.
        Args:
            request (flask.Request): The request object.
        Returns:
            Code 200 if successful, Code 500 if an error occurs.
    """
    if not GCP_PROJECT_ID:
        raise ValueError("GCP_PROJECT_ID not set in .env file")
    if not GCS_BUCKET_NAME:
        raise ValueError("GCS_BUCKET_NAME not set in .env file")
    
    try:
        
        census_df = bronze.extract_census_data(IOWA_CENSUS_URL)
        print(f"✓ Extracted {len(census_df)} rows of census data")

        print(f"✓ Uploading raw data to GCS bucket: {GCS_BUCKET_NAME}...")

        census_path = f"gs://{GCS_BUCKET_NAME}/bronze/census/iowa_census.parquet"
        census_df.to_parquet(census_path, index = False)
        print(f"✓ Uploaded census data to {census_path}")

        return "Extraction completed successfully", 200 
    except Exception as e:
        print(f"Error: {e}")
        return f"Internal Error: {e}", 500