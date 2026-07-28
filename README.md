# Iowa Liquor Sales & Census Data ETL Pipeline

ETL pipeline that extracts, transforms, and validates Iowa liquor sales and census data, combining BigQuery public datasets with information from the Iowa Data Portal. 

This project implements a Medallion Architecture (Bronze, Silver, Gold) for robust data processing.

## 📋 Overview

This project implements a complete ETL pipeline that:

1. **Extracts (Bronze)** Iowa liquor sales data from BigQuery and population census data from the Iowa Data Portal API.
2. **Cleans (Silver)** and normalizes both datasets, handling missing values and data types.
3. **Transforms (Gold)** data into three distinct analysis tables.
4. **Optimizes Memory** by freeing large raw dataframes before validation.
5. **Validates** data quality with automated checks on the final analytical tables.
6. **Reports** validation results with error severities.

## 🎯 Pipeline Flow (Medallion Architecture)

```
Extract (Bronze) → Clean (Silver) → Transform (Gold) → Validate → Report
```

## 📊 Output Tables Generated (Gold Layer)

### 1. **Country Sales Summary**
- **Granularity**: By year and county
- **Metrics**:
  - `total_gallons_told`: Total gallons sold
  - `total_sales_dollars`: Total sales in USD
  - `county_population`: County population
  - `sales_per_capita`: Sales per capita (derived)
- **Use**: Geographic sales performance analysis

### 2. **Store and Product Analysis**
- **Granularity**: By year, month, store, and product category
- **Metrics**:
  - `total_sales_dollars`: Total sales in USD
  - `total_bottles_sold`: Total bottles sold
- **Use**: Store and product category performance analysis

### 3. **Price Inflation Tracker**
- **Granularity**: By year, month, and product category
- **Metrics**:
  - `total_sales`: Total sales in USD
  - `total_liters_sold`: Total liters sold
  - `average_price_per_liter`: Average price per liter (derived). *Note: Includes robust handling using `numpy.where` to prevent division by zero or nulls.*
- **Use**: Price inflation tracking by category

## ✅ Data Quality Validation

The pipeline includes automated validations for each final analytical table:

| Check | Severity | Description |
|-------|----------|-------------|
| NULL_VALUES | HIGH | Detects missing/null values in any column |
| NEGATIVE_VALUES | HIGH | Detects negative values in numeric columns |
| DUPLICATES | MEDIUM | Detects completely duplicate rows |
| EMPTY_TABLE | HIGH | Verifies table contains data |

**Note**: If critical failures (HIGH severity) are found, the pipeline stops execution.

## 🔧 Prerequisites

- **Python** 3.8+
- **Google Cloud Project** with BigQuery enabled
- **gcloud CLI** configured with appropriate credentials
- **Libraries**: `google-cloud-bigquery`, `pandas`, `requests`, `python-dotenv`, `numpy`

## 📦 Installation and Execution

### Step 1: Clone the repository

```bash
git clone <repository-url>
cd bg_technical_challenge
```

### Step 2: Create virtual environment

**On Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create a `.env` file in the project root:
```
GCP_PROJECT_ID=your-gcp-project-here
```

### Step 5: Authenticate with Google Cloud

```bash
gcloud auth login
gcloud config set project your-gcp-project
gcloud auth application-default login
```

### Step 6: Run the pipeline

```bash
python3 main.py
```

### Expected Output:
```
✓ BigQuery client initialized
✓ Project ID: your-gcp-project
✓ Extracting Iowa Liquor Sales data from BigQuery...
✓ Extracted X rows of liquor sales data
✓ Extracting Iowa Census data from Data Portal...
✓ Extracted Y rows of census data
✓ Cleaning liquor data...
✓ Liquor data cleaned
✓ Cleaning Census data...
✓ Census Data cleaned

--- TRANSFORMATION ---
✓ Transforming and joining datasets...
✓ Transformed country_sales_summary_df created with X rows
✓ Transformed store_and_product_analysis_df created with Y rows
✓ Transformed price_inflation_tracker_df created with Z rows

--- DATA QUALITY CHECKS ---

Validating: Country Sales Summary
  ✓ NULL_VALUES: No null values found
  ...
```

## 📡 Data Sources

### BigQuery Public Data
- **Dataset**: `bigquery-public-data.iowa_liquor_sales.sales`
- **Fields Extracted**: `invoice_and_item_number`, `date`, `county`, `store_name`, `category_name`, `volume_sold_liters`, `volume_sold_gallons`, `sale_dollars`, `bottles_sold`
- **Filters**: Last 3 fiscal years.

### Iowa Data Portal API
- **URL**: `https://data.iowa.gov/api/dataset-download?path=datasets%2F707%2Frows.json`
- **Data**: County population by year.
- **Fields**: `calendar_year`, `geographic_name`, `population`

## 🔍 Cleaning Processes (Silver Layer)

### Liquor Sales Data
1. Extraction of year and month as integer fields (int32).
2. Handling null values in the `county` column by replacing them with `"NO DATA"`.

### Census Data
1. Renaming columns (`calendar_year` → `year`, `geographic_name` → `county`).
2. Normalization of county names (removal of the word " County").
3. Capitalization of names.
4. Conversion of year to int32.

## 🛠 Code Structure

The code is strictly organized into functional layers:

| Layer | Function | Description |
|-------|----------|-------------|
| **Setup** | `get_bigquery_client()` | Initializes the BigQuery client |
| **Bronze** | `extract_liquor_sales(client)` | Extracts raw sales data from BigQuery |
| **Bronze** | `extract_census_data()` | Extracts raw census data from the API |
| **Silver** | `clean_liquor_data(liquor_df)` | Cleans and normalizes liquor sales data |
| **Silver** | `clean_census_data(census_df)` | Cleans and normalizes census data |
| **Gold** | `create_country_sales_summary_df(...)` | Generates the geographic sales summary table |
| **Gold** | `create_store_and_product_analysis_df(...)` | Generates the store & product analytical table |
| **Gold** | `create_price_inflation_tracker_df(...)` | Generates the inflation tracker table (handles div/0) |
| **DQ** | `validate_table_quality(df, table_name)` | Performs the automated Data Quality assertions |

*Note on Memory Management: Once the Gold analytical tables are generated, the pipeline actively frees up memory by deleting the large `liquor_df` and `census_df` dataframes (`del liquor_df, census_df`) before proceeding to the data quality checks.*

## 📝 Advanced Usage Examples

### Filter by specific store
```python
# Assuming you import store_and_product_analysis_df from main
tienda_filter = store_and_product_analysis_df[
    (store_and_product_analysis_df["year"] == 2024) & 
    (store_and_product_analysis_df["month"] == 10) &
    (store_and_product_analysis_df["store_name"] == 'HY-VEE #3')
]
print(tienda_filter)
```

## ⚠️ Important Notes

- Negative values in `bottles_sold` and `sale_dollars` might indicate returns or adjustments in the original dataset.
- A stable internet connection is required to fetch data from BigQuery and the API.
- Your GCP credentials must have read access to `bigquery-public-data`.

## 🐛 Troubleshooting

- **Error: "GCP_PROJECT_ID not set"**: Ensure your `.env` file exists and contains the variable.
- **Error: "Authentication failed"**: Run `gcloud auth application-default login` again.
