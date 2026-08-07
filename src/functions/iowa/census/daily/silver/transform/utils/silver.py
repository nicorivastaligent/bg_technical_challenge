import pandas as pd
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

def clean_census_data(census_df):
    """
    Clean and normalize census dataset (capitalize counties, convert year to integer, rename columns).
    
    Args:
        census_df (pd.DataFrame): Raw census data.
    
    Returns:
        pd.DataFrame: Cleaned census data.
    """

    census_df = census_df.rename(columns={'calendar_year': 'year', 'geographic_name': 'county'})
    census_df['county'] = census_df['county'].str.replace(' County', '').str.capitalize()
    census_df["year"] = pd.to_datetime(census_df["year"]).dt.year.astype("int32")
    print(f"✓ Cleaned census data")

    return census_df

def upload_to_bigquery(df, table_name, client, GCP_PROJECT_ID):
    """
    Upload a Pandas DataFrame to BigQuery in Silver layer with overwrite disposition.

    Args:
        df (pd.DataFrame): Dataframe to load into BigQuery.
        table_name (str): Target table name in Silver dataset.
        client (bigquery.Client): BigQuery client object.
        GCP_PROJECT_ID (str): GCP project ID.

    Returns:
        google.cloud.bigquery.job.LoadJob: Load job execution result.
    """
    table_id = f"{GCP_PROJECT_ID}.dev_taligent_bg_technicall_challenge_iowa_silver.{table_name}"
    # Load configuration
    job_config = bigquery.LoadJobConfig(
        # Overwrite disposition if table exists
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    # Load DataFrame into BigQuery
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # Wait for job completion
    print(f"✓ Uploaded cleaned {table_name} data to table {table_id} in BigQuery")
    return job

def incremental_load_to_bigquery_liquor(client, GCP_PROJECT_ID):
    """
    Perform an incremental MERGE load of liquor sales data from public dataset to BigQuery Silver layer.

    Args:
        client (bigquery.Client): BigQuery client object.
        GCP_PROJECT_ID (str): GCP project ID.
    """
    target_table = f"{GCP_PROJECT_ID}.dev_taligent_bg_technicall_challenge_iowa_silver.liquor_sales_data"
    public_table = "bigquery-public-data.iowa_liquor_sales.sales"

    job_config = bigquery.QueryJobConfig(
        default_dataset=f"{GCP_PROJECT_ID}.dev_taligent_bg_technicall_challenge_iowa_silver"
    )

    source_query = f"""SELECT 
        invoice_and_item_number,
        date,
        EXTRACT(YEAR FROM date) AS year,
        EXTRACT(MONTH FROM date) AS month,
        IFNULL(county, 'NO DATA') AS county,
        store_name,
        category_name,
        volume_sold_liters,
        volume_sold_gallons,
        sale_dollars,
        bottles_sold
    FROM `{public_table}` WHERE EXTRACT(YEAR FROM date) > (EXTRACT(YEAR FROM CURRENT_DATE())-3) 
    ORDER BY date DESC, invoice_and_item_number DESC """

    try:
        client.get_table(target_table)
        print(f"✓ The table {target_table} already exists. Proceeding with MERGE...")

        merge_query = f"""
        MERGE `{target_table}` target
        USING ({source_query}) source
        ON target.invoice_and_item_number = source.invoice_and_item_number
        WHEN MATCHED THEN
            UPDATE SET
                target.date = source.date,
                target.year = source.year,
                target.month = source.month,
                target.county = source.county,
                target.store_name = source.store_name,
                target.category_name = source.category_name,
                target.volume_sold_liters = source.volume_sold_liters,
                target.volume_sold_gallons = source.volume_sold_gallons,
                target.sale_dollars = source.sale_dollars,
                target.bottles_sold = source.bottles_sold
        WHEN NOT MATCHED THEN
            INSERT ROW
        """

        client.query(merge_query, job_config=job_config).result()

    except NotFound:
        print(f"⚠️ {target_table} table not found. Creating the table and loading data...")
    
        # La crea por primera vez copiando los datos/esquema de Staging
        create_table_query = f"""
        CREATE TABLE `{target_table}` AS
        {source_query};
        """
        client.query(create_table_query, job_config=job_config).result()

    print("✓ Liquor sales incremental load completed successfully.")
