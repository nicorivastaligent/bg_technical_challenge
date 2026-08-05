import utils.bronze as bronze
from dotenv import load_dotenv
import os 

load_dotenv()
IOWA_CENSUS_URL = "https://data.iowa.gov/api/dataset-download?path=datasets%2F707%2Frows.json"

def main(request):
    """
        Cloud Function to extract Iowa census population data from Iowa Data Portal API and upload it to GCS bucket.
        Args:
            request (flask.Request): The request object.
        Returns:
            Code 200 if successful, Code 500 if an error occurs.
    """
    gcp_project_id = os.environ.get("GCP_PROJECT_ID")
    gcs_bucket_name = os.environ.get("GCS_BUCKET_NAME")

    if not gcp_project_id:
        raise ValueError("gcp_project_id not set in .env file")
    if not gcs_bucket_name:
        raise ValueError("gcs_bucket_name not set in .env file")
    
    try:
        
        census_df = bronze.extract_census_data(IOWA_CENSUS_URL)
        print(f"✓ Extracted {len(census_df)} rows of census data")

        print(f"✓ Uploading raw data to GCS bucket: {gcs_bucket_name}...")

        census_path = f"gs://{gcs_bucket_name}/bronze/census/iowa_census.parquet"
        census_df.to_parquet(census_path, index = False)
        print(f"✓ Uploaded census data to {census_path}")

        return "Extraction completed successfully", 200 
    except Exception as e:
        print(f"Error: {e}")
        return f"Internal Error: {e}", 500