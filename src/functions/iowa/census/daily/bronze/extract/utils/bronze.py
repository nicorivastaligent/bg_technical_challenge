import requests
import pandas as pd

def extract_census_data(IOWA_CENSUS_URL):
    """
    Extract Iowa census population data from Iowa Data Portal API.
    
    Args:
        IOWA_CENSUS_URL (str): URL of the Iowa Data Portal API endpoint for census data.
    
    Returns:
        pd.DataFrame: Census data with calendar_year, geographic_name, and population columns.
    """
    response = requests.get(IOWA_CENSUS_URL)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)

    return df