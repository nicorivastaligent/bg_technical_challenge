# bg_technical_challenge

ETL pipeline to extract, transform, and load Iowa liquor sales and census data into BigQuery.

## Overview

This project processes Iowa liquor sales data from BigQuery public datasets combined with Iowa census population data from the Iowa Data Portal. The pipeline cleans, joins, and creates three output tables for analysis.

## Setup

### Prerequisites

- Python 3.14+
- Google Cloud Project with BigQuery enabled
- gcloud CLI configured with appropriate credentials

### Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env and add your GCP_PROJECT_ID
   ```

4. Authenticate with Google Cloud:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

## Usage

Run the ETL pipeline:
```bash
python main.py
```

## Data Sources

- **Liquor Sales**: BigQuery public dataset `bigquery-public-data.iowa_liquor_sales.sales` (last 3 years)
- **Census Data**: Iowa Data Portal API (https://data.iowa.gov/api/views/707/rows.csv)

## Project Structure

```
.
├── main.py              # ETL pipeline implementation
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```
