def create_country_sales_summary_df(client, liquor_table, census_table):
    """
    Create Country Sales Summary analysis table in BigQuery.
    
    Args:
        client (bigquery.Client): BigQuery client.
        liquor_table (str): BigQuery table ID for cleaned liquor sales data.
        census_table (str): BigQuery table ID for cleaned census data.
    """
    query = f"""
    CREATE OR REPLACE TABLE `bg-technicall-challenge.dev_taligent_bg_technicall_challenge_iowa_gold.country_sales_summary` AS
    SELECT
        liquor.year,
        liquor.county,
        liquor.total_Gallons_told,
        liquor.total_sales_dollars,
        CASE
            WHEN census.population IS NULL
            THEN 0
            ELSE census.population
        END AS population,
        CASE
            WHEN census.population IS NULL OR census.population = 0
            THEN 0.0
            ELSE liquor.total_sales_dollars / census.population
        END AS sales_per_capita
    FROM(
        SELECT 
            year,
            INITCAP(county) AS county,
            SUM(volume_sold_gallons)    AS total_Gallons_told,
            SUM(sale_dollars)           AS total_sales_dollars
        FROM `{liquor_table}` 
        GROUP BY year, county
    ) as liquor
    LEFT JOIN `{census_table}` as census
    ON liquor.county = census.county AND liquor.year = census.year"""

    client.query(query).result()  # Wait for the query to finish
    print("✓ Country Sales Summary table updated successfully in BigQuery.")

def create_store_and_product_analysis_df(client, liquor_table):
    """
        Create Store and product analytics table in BigQuery.
        
        Args:
            client (bigquery.Client): BigQuery client.
            liquor_table (str): BigQuery table ID for cleaned liquor sales data.
    """

    query = f"""
    CREATE OR REPLACE TABLE `bg-technicall-challenge.dev_taligent_bg_technicall_challenge_iowa_gold.store_and_product_analysis` AS
    SELECT 
        year,
        month,
        store_name,
        category_name,
        SUM(sale_dollars)   AS total_sales_dollars,
        SUM(bottles_sold)   AS total_bottles_sold
    FROM `{liquor_table}` 
    GROUP BY year, month, store_name, category_name"""

    client.query(query).result()  # Wait for the query to finish
    print("✓ Store and Product Analysis table updated successfully in BigQuery.")

def create_price_inflation_tracker_df(client, liquor_table):
    """
            Create Price Inflation Tracker table.
            
            Args:
                client (bigquery.Client): BigQuery client.
                liquor_table (str): BigQuery table ID for cleaned liquor sales data.
    """
    query = f"""
    CREATE OR REPLACE TABLE `bg-technicall-challenge.dev_taligent_bg_technicall_challenge_iowa_gold.price_inflation_tracker` AS
    SELECT 
        year,
        month,
        county,
        category_name,
        CASE
            WHEN SUM(volume_sold_liters) = 0 OR SUM(volume_sold_liters) IS NULL
            THEN 0
            ELSE SUM(sale_dollars) / SUM(volume_sold_liters)
        END AS average_price_per_liter
    FROM `{liquor_table}` 
    GROUP BY year, month, county, category_name"""
    
    client.query(query).result()  # Wait for the query to finish
    print("✓ Price Inflation Tracker table updated successfully in BigQuery.")