"""
Iowa Liquor Sales & Census Data ETL Pipeline.

Extracts data from BigQuery and Iowa Data Portal, cleans, transforms into 3 analysis tables,
and validates data quality with automated checks.
Requires: GCP_PROJECT_ID environment variable.
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
    Initialize authenticated BigQuery client using GCP_PROJECT_ID.
    
    Returns:
        bigquery.Client: Authenticated BigQuery client.
    """
    return bigquery.Client(project=GCP_PROJECT_ID)

""" ------ Bronze layer -------  """
def extract_liquor_sales(client):
    """
    Extract Iowa liquor sales from BigQuery (last 3 years, limit 100K rows).
    
    Args:
        client (bigquery.Client): BigQuery client.
    
    Returns:
        pd.DataFrame: Sales data with date, county, store, category, volume, and amount columns.
    """
    query = """SELECT 
        invoice_and_item_number,
        date,
        county,
        store_name,
        category_name,
        volume_sold_liters,
        volume_sold_gallons,
        sale_dollars,
        bottles_sold
    FROM `bigquery-public-data.iowa_liquor_sales.sales` WHERE EXTRACT(YEAR FROM date) > (EXTRACT(YEAR FROM CURRENT_DATE())-2) 
    order by date, county, store_name, category_name"""
    query_job = client.query(query)
    df = query_job.to_dataframe()

    return df

def extract_census_data():
    """
    Extract Iowa census population data from Iowa Data Portal API.
    
    Returns:
        pd.DataFrame: Census data with calendar_year, geographic_name, and population columns.
    """
    response = requests.get(IOWA_CENSUS_URL)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)

    return df

""" ------ Silver layer -------  """
def clean_census_data(census_df):
    """
    Clean and normalize both datasets (capitalize counties, extract year/month, rename columns).
    
    Args:
        census_df (pd.DataFrame): Raw census data.
    
    Returns:
        tuple: (cleaned_liquor_df, cleaned_census_df)
    """

    census_df = census_df.rename(columns={'calendar_year': 'year', 'geographic_name': 'county'})
    census_df['county'] = census_df['county'].str.replace(' County', '').str.capitalize()
    census_df["year"] = pd.to_datetime(census_df["year"]).dt.year.astype("int32")

    return census_df

def clean_liquor_data(liquor_df):
    """
    Clean and normalize both datasets (capitalize counties, extract year/month, rename columns).
    
    Args:
        liquor_df (pd.DataFrame): Raw liquor sales data.
    
    Returns:
        tuple: (cleaned_liquor_df, cleaned_census_df)
    """
    liquor_df['county'] = liquor_df['county'].str.capitalize()
    liquor_df["year"] = pd.to_datetime(liquor_df["date"]).dt.year.astype("int32")
    liquor_df["month"] = pd.to_datetime(liquor_df["date"]).dt.month.astype("int32")

    return liquor_df

""" ------ Gold layer -------  """
def create_country_sales_summary_df(liquor_df, census_df):
    """
    Create Country Sales Summary analysis table.
    
    Args:
        liquor_df (pd.DataFrame): Cleaned liquor sales data.
        census_df (pd.DataFrame): Cleaned census data.
    
    Returns:
        data frame: country_sales_summary_df
    """
    country_sales_summary_df = liquor_df[["year","county","volume_sold_gallons","sale_dollars"]]
    country_sales_summary_df = country_sales_summary_df.merge(census_df[['county','year','population']], on=['year','county'], how='left')
    country_sales_summary_df = country_sales_summary_df.groupby(["year","county"], as_index = False).agg(
        total_tallons_told=("volume_sold_gallons", "sum"),
        total_sales_dollars=("sale_dollars", "sum"),
        county_population=("population", "sum")
    )
    country_sales_summary_df["sales_per_capita"] = country_sales_summary_df["total_sales_dollars"] / country_sales_summary_df["county_population"]

    return country_sales_summary_df

def create_store_and_product_analysis_df(liquor_df):
    """
        Create Store and product analytics table.
        
        Args:
            liquor_df (pd.DataFrame): Cleaned liquor sales data.
        
        Returns:
            data frame: store_and_product_analysis_df
    """
    store_and_product_analysis_df = liquor_df[["year","month","store_name","category_name","sale_dollars","bottles_sold"]]
    store_and_product_analysis_df = store_and_product_analysis_df.groupby(["year","month","store_name","category_name"], as_index = False).agg(
        total_sales_dollars = ("sale_dollars", "sum"),
        total_bottles_sold = ("bottles_sold", "sum")
    )

    return store_and_product_analysis_df

def create_price_inflation_tracker_df(liquor_df):
    """
            Create Price Inflation Tracker table.
            
            Args:
                liquor_df (pd.DataFrame): Cleaned liquor sales data.
            
            Returns:
                data frame: price_inflation_tracker_df
    """
    price_inflation_tracker_df = liquor_df[["year","month","county","category_name","sale_dollars","volume_sold_liters"]]
    price_inflation_tracker_df = price_inflation_tracker_df.groupby(["year","month","county","category_name"], as_index = False).agg(
        total_sales = ("sale_dollars", "sum"),
        total_liters_sold = ("volume_sold_liters", "sum")
    )
    price_inflation_tracker_df["average_price_per_liter"] = price_inflation_tracker_df["total_sales"] / price_inflation_tracker_df["total_liters_sold"]
    price_inflation_tracker_df = price_inflation_tracker_df[["year","month","county","category_name","average_price_per_liter"]]

    return price_inflation_tracker_df

""" ------ Data Quality -------  """
def validate_table_quality(df, table_name):
    """
    Validate data quality with 4 checks: nulls, negatives, duplicates, and empty table.
    
    Args:
        df (pd.DataFrame): Table to validate.
        table_name (str): Name of the table for reporting.
    
    Returns:
        dict: Report with status, checks_performed, failures, and summary metrics.
    """
    dq_report = {
        "table_name": table_name,
        "status": "PASS",
        "checks_performed": [],
        "failures": []
    }

    # Check 1: Null values
    null_counts = df.isna().sum()
    null_failures = {col: int(count) for col, count in null_counts[null_counts > 0].items()}

    if null_failures:
        dq_report["status"] = "FAIL"
        dq_report["failures"].append({
            "check": "NULL_VALUES",
            "severity": "HIGH",
            "details": null_failures
        })
    else:
        dq_report["checks_performed"].append(f"✓ NULL_VALUES: No null values found")

    # Check 2: Negative values in numerical columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    negative_counts = {}
    for col in numeric_cols:
        neg_count = (df[col] < 0).sum()
        if neg_count > 0:
            negative_counts[col] = int(neg_count)

    if negative_counts:
        dq_report["status"] = "FAIL"
        dq_report["failures"].append({
            "check": "NEGATIVE_VALUES",
            "severity": "HIGH",
            "details": negative_counts
        })
    else:
        dq_report["checks_performed"].append(f"✓ NEGATIVE_VALUES: No negative values in numerical columns")

    # Check 3: Duplicates (check all columns for duplicates)
    duplicates_count = df.duplicated().sum()

    if duplicates_count > 0:
        dq_report["status"] = "FAIL"
        dq_report["failures"].append({
            "check": "DUPLICATES",
            "severity": "CRITICAL",
            "details": f"{duplicates_count} duplicate rows found"
        })
    else:
        dq_report["checks_performed"].append(f"✓ DUPLICATES: No duplicate records found")

    # Check 4: Empty dataframe
    if len(df) == 0:
        dq_report["status"] = "FAIL"
        dq_report["failures"].append({
            "check": "EMPTY_TABLE",
            "severity": "HIGH",
            "details": "Table is empty (0 rows)"
        })
    else:
        dq_report["checks_performed"].append(f"✓ EMPTY_TABLE: Table has {len(df)} rows")

    # Summary
    dq_report["summary"] = {
        "total_checks": len(dq_report["checks_performed"]) + len(dq_report["failures"]),
        "passed_checks": len(dq_report["checks_performed"]),
        "failed_checks": len(dq_report["failures"]),
        "rows": len(df),
        "columns": len(df.columns)
    }

    return dq_report

if __name__ == "__main__":
    if not GCP_PROJECT_ID:
        raise ValueError("GCP_PROJECT_ID not set in .env file")

    try:
        client = get_bigquery_client()
        print(f"✓ BigQuery client initialized")
        print(f"✓ Project ID: {GCP_PROJECT_ID}")
        
        print(f"✓ Extracting Iowa Liquor Sales data from BigQuery...")
        liquor_df = extract_liquor_sales(client)
        # print(f"✓ Extracted {len(liquor_df)} rows of liquor sales data")

        print(f"✓ Extracting Iowa Census data from Data Portal...")
        census_df = extract_census_data()
        print(f"✓ Extracted {len(census_df)} rows of census data")

        print(f"✓ Cleaning liquor data...")
        liquor_df = clean_liquor_data(liquor_df)
        print(f"✓ Liquor data cleaned")
        
        print(f"✓ Cleaning Census data...")
        census_df = clean_census_data(census_df)
        print(f"✓ Census Data cleaned")

        print(f"\n--- TRANSFORMATION ---")
        print(f"✓ Transforming and joining datasets...")
        country_sales_summary_df = create_country_sales_summary_df(liquor_df, census_df)
        print(f"✓ Transformed country_sales_summary_df created with {len(country_sales_summary_df)} rows")
        store_and_product_analysis_df = create_store_and_product_analysis_df(liquor_df)
        print(f"✓ Transformed store_and_product_analysis_df created with {len(store_and_product_analysis_df)} rows")
        price_inflation_tracker_df = create_price_inflation_tracker_df(liquor_df)
        print(f"✓ Transformed price_inflation_tracker_df created with {len(price_inflation_tracker_df)} rows")

        print(f"\n--- DATA QUALITY CHECKS ---")
        
        # Validate each table individually
        dq_reports = []
        tables_to_validate = [
            (liquor_df, "Liquor Sales Raw Data"),
            (census_df, "Census Raw Data"),
            (country_sales_summary_df, "Country Sales Summary"),
            (store_and_product_analysis_df, "Store and Product Analysis"),
            (price_inflation_tracker_df, "Price Inflation Tracker")
        ]
        
        for table_df, table_name in tables_to_validate:
            print(f"\nValidating: {table_name}")
            dq_report = validate_table_quality(table_df, table_name)
            dq_reports.append(dq_report)
            
            # Print DQ results
            for check in dq_report["checks_performed"]:
                print(f"  {check}")
            
            if dq_report["failures"]:
                print(f"  ⚠ Failures Detected:")
                for failure in dq_report["failures"]:
                    print(f"    ✗ {failure['check']} (Severity: {failure['severity']}): {failure['details']}")
            
            print(f"  Summary: {dq_report['summary']}")
                
            # Raise exception if critical failures found
            critical_failures = [f for f in dq_report["failures"] if f["severity"] == "CRITICAL"]
            if critical_failures:
                raise ValueError(f"Data quality check failed for {table_name}: {len(critical_failures)} critical issue(s) found")
            
    except Exception as e:
        print(f"✗ Error: {e}")
