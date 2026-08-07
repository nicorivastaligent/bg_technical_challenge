# Iowa Liquor Sales & Census Data ETL Pipeline (GCP Cloud Functions)

This project implements a Medallion Architecture (Bronze, Silver, Gold) for robust data processing of Iowa liquor sales and census data. It extracts data from BigQuery public datasets and the Iowa Data Portal, transforms it, and loads it back into BigQuery for analysis.

**Major Update:** The pipeline has been completely refactored to run as modular **Google Cloud Functions** rather than a single monolithic script. It now utilizes Google Cloud Storage (GCS) for raw data staging and BigQuery for data transformation and storage.

## 📋 Overview

This project implements a complete ETL pipeline divided into independent Cloud Functions:

1. **Extract (Bronze - Census):** Extracts population census data from the Iowa Data Portal API and stores the raw data as a Parquet file in a GCS bucket.
2. **Transform & Incremental Load (Silver):**
   - Cleans the census data from GCS and loads it into a BigQuery Silver table.
   - Performs an **incremental load (MERGE)** of the liquor sales data from the public BigQuery dataset into a BigQuery Silver table.
3. **Transform for Analysis (Gold):** Executes SQL queries directly within BigQuery to generate three distinct analysis tables based on the Silver data.

## 🎯 Pipeline Flow (Medallion Architecture)

```
Cloud Function (Bronze) -> GCS Bucket (Raw Parquet)
                                    |
                                    v
Cloud Function (Silver) -> BigQuery (Cleaned Tables + Incremental Liquor Load)
                                    |
                                    v
Cloud Function (Gold)   -> BigQuery (Analytical Tables)
```

## 📊 Output Tables Generated (Gold Layer)

The Gold Cloud Function generates the following tables directly in BigQuery:

### 1. `county_sales_summary` (in code: `country_sales_summary`)
- **Granularity**: By year and county
- **Metrics**: `total_Gallons_told`, `total_sales_dollars`, `population`, `sales_per_capita`
- **Use**: Geographic sales performance analysis

### 2. `store_and_product_analysis`
- **Granularity**: By year, month, store, and product category
- **Metrics**: `total_sales_dollars`, `total_bottles_sold`
- **Use**: Store and product category performance analysis

### 3. `price_inflation_tracker`
- **Granularity**: By year, month, county, and product category
- **Metrics**: `average_price_per_liter` (handles division by zero/nulls)
- **Use**: Price inflation tracking by category

## 🔧 Prerequisites

- **Python** 3.8+
- **Google Cloud Project** with BigQuery and Cloud Storage enabled.
- **gcloud CLI** configured with appropriate credentials.
- A GCS bucket for staging raw data (e.g., `dev-taligent-bg-technicall-challenge-gcs-bronze`).
- BigQuery datasets created for the Silver and Gold layers.

## 🚀 Instructions: How to Run the Code

Since the architecture is based on independent Google Cloud Functions, you can run them either locally using the Functions Framework or deploy them directly to Google Cloud. 

First, ensure you have authenticated your local environment:
```bash
gcloud auth application-default login
gcloud config set project your-gcp-project-id
```

### Option A: Run Locally (Functions Framework)

You will need to run this process for each layer's directory. Here is an example for the Bronze layer:

1. **Navigate to the specific function's directory:**
   ```bash
   cd src/functions/iowa/census/daily/bronze/extract
   ```

2. **Set up your environment variables:**
   Create a `.env` file in that directory containing:
   ```
   GCP_PROJECT_ID=your-gcp-project-id
   GCS_BUCKET_NAME=your-gcs-bucket-name
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the function locally:**
   ```bash
   functions-framework --target=main --debug
   ```
   *The function will start a local server (usually on port 8080). You can trigger it by navigating to `http://localhost:8080` in your browser or using `curl http://localhost:8080`.*

### Option B: Deploy to Google Cloud

To deploy a function to your GCP environment, run the following command from within the specific function's directory (e.g., inside `bronze/extract`):

```bash
gcloud functions deploy etl_bronze_extract   --runtime python311   --trigger-http   --entry-point main   --source .   --set-env-vars GCP_PROJECT_ID=your-gcp-project-id,GCS_BUCKET_NAME=your-gcs-bucket-name
```
*(Repeat this deployment process for the Silver and Gold directories, adjusting the environment variables as needed).*

## 📦 Deployment Structure

The project is structured to be deployed as separate HTTP-triggered Google Cloud Functions. Each layer (Bronze, Silver, Gold) has its own directory with a `main.py` and `requirements.txt`.

```
src/functions/iowa/
├── census/daily/
│   ├── bronze/extract/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── utils/bronze.py
│   ├── silver/transform/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── utils/silver.py
│   └── gold/create/
│       ├── main.py
│       ├── requirements.txt
│       └── utils/gold.py
```

## 📡 Data Sources

### BigQuery Public Data
- **Dataset**: `bigquery-public-data.iowa_liquor_sales.sales`
- **Filters**: Last 3 fiscal years (`EXTRACT(YEAR FROM date) > (EXTRACT(YEAR FROM CURRENT_DATE())-3)`).

### Iowa Data Portal API
- **URL**: `https://data.iowa.gov/api/dataset-download?path=datasets%2F707%2Frows.json`

## 🔍 Data Processing Details

### Bronze Layer (Census Extraction)
- Fetches data from the Iowa Data Portal API.
- Saves the raw JSON response as a Parquet file in GCS (`gs://[BUCKET_NAME]/bronze/census/iowa_census.parquet`).

### Silver Layer (Cleaning & Incremental Load)
- **Census Data:** Reads the Parquet file from GCS. Renames columns (`calendar_year` -> `year`, `geographic_name` -> `county`), removes " County" from names, capitalizes them, and converts the year to `int32`. Uploads the cleaned dataframe to BigQuery (Truncate and Load).
- **Liquor Data:** Performs a BigQuery-native `MERGE` operation. It selects data from the public dataset for the last 3 years and inserts new rows or updates existing ones based on `invoice_and_item_number` in the target Silver table. If the target table doesn't exist, it creates it.

### Gold Layer (Transformations)
- Executes `CREATE OR REPLACE TABLE` SQL queries within BigQuery to build the final analytical tables by joining and aggregating the Silver tables.

## 🗺️ Roadmap / Future Improvements

- **Further Modularization**: Split table transformations (such as liquor sales transformations) into dedicated, independent functions/modules, reflecting separate Cloud Run / Cloud Function deployments for higher scalability and isolation.
- **Dynamic Configuration & Parameterization**: Remove hardcoded bucket names and BigQuery datasets, replacing them with dynamic environment variables or GCP Secret Manager.
- **Data Quality & Testing**: Integrate data quality check frameworks (e.g., dbt tests or Great Expectations) to validate data schemas and nulls prior to Silver/Gold loading.
- **CI/CD Automation**: Implement GitHub Actions workflows for automated linting, unit testing, and deployment to GCP environments.

## ⚠️ Important Notes
- The current structure hardcodes some GCS paths (e.g., in `silver/transform/main.py`: `"gs://dev-taligent-bg-technicall-challenge-gcs-bronze/..."`) and BigQuery Dataset names (e.g., `dev_taligent_bg_technicall_challenge_iowa_silver`, `bg-technicall-challenge.dev_taligent_bg_technicall_challenge_iowa_gold`). You will need to update these to match your GCP environment.
