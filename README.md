# Iowa Liquor Sales & Census Data ETL Pipeline

ETL pipeline that extracts, transforms, and validates Iowa liquor sales and census data, combining BigQuery public datasets with information from the Iowa Data Portal.

## 📋 Overview

This project implements a complete ETL pipeline that:

1. **Extracts** Iowa liquor sales data from BigQuery (last 3 years, max 100,000 records)
2. **Extracts** Iowa population census data from the Iowa Data Portal API
3. **Cleans** and normalizes both datasets
4. **Transforms** data into three distinct analysis tables
5. **Validates** data quality with automated checks
6. **Reports** validation results with error severities

## 🎯 Pipeline Flow

```
Extract (BigQuery + API) → Clean → Transform → Validate → Report
```

## 📊 Output Tables Generated

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
  - `average_price_per_liter`: Average price per liter (derived)
- **Use**: Price inflation tracking by category

## ✅ Data Quality Validation

The pipeline includes automated validations for each table:

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
- **Libraries**: google-cloud-bigquery, pandas, requests, python-dotenv

## 📦 Installation and Execution

### Step 1: Prepare folder structure

```bash
# Create project folder (optional)
mkdir -p ~/projects
cd ~/projects
```

### Step 2: Clone the repository

```bash
git clone <repository-url>
cd bg_technical_challenge
```

Project structure:
```
bg_technical_challenge/
├── main.py                    # Main pipeline script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .env                       # Environment variables (create)
├── .venv/                     # Virtual environment (create)
└── .gitignore
```

### Step 3: Create virtual environment

**On Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows (CMD):**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

You should see `(.venv)` at the beginning of your command line when activated.

### Step 4: Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Dependencies installed:
- `google-cloud-bigquery`: BigQuery access
- `pandas`: Data manipulation
- `requests`: HTTP requests to Iowa Data Portal
- `python-dotenv`: Environment variable management

Verify installation:
```bash
pip list
```

### Step 5: Configure environment variables

Create `.env` file in the project root:
```bash
cp .env.example .env  # If it exists, or create manually
```

Edit `.env` and add your GCP Project ID:
```
GCP_PROJECT_ID=your-gcp-project-here
```

**Note**: Do not commit `.env` to repository (should be in `.gitignore`)

### Step 6: Authenticate with Google Cloud

Option A - Using gcloud CLI (recommended for development):
```bash
gcloud auth login
gcloud config set project your-gcp-project
gcloud auth application-default login
```

Option B - Using credentials file (for production):
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

### Step 7: Run the pipeline

```bash
python3 main.py
```

**Expected output:**
```
✓ BigQuery client initialized
✓ Project ID: your-gcp-project
✓ Extracting Iowa Liquor Sales data from BigQuery...
✓ Extracting Iowa Census data from Data Portal...
✓ Cleaning data...

--- TRANSFORMATION ---
✓ Transformed country_sales_summary_df created with X rows
✓ Transformed store_and_product_analysis_df created with Y rows
✓ Transformed price_inflation_tracker created with Z rows

Validating: Liquor Sales Raw Data
  ✓ NULL_VALUES: No null values found
  ✓ NEGATIVE_VALUES: No negative values in numerical columns
  ✓ DUPLICATES: No duplicate records found
  ✓ EMPTY_TABLE: Table has N rows
  Summary: {...}
```

## 🔄 Complete Workflow

**Command summary:**

```bash
# 1. Clone and enter directory
git clone <repository-url>
cd bg_technical_challenge

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure Google Cloud credentials
gcloud auth application-default login
gcloud config set project your-gcp-project

# 5. Create .env file
echo "GCP_PROJECT_ID=your-gcp-project" > .env

# 6. Run pipeline
python3 main.py
```

## 🔒 Security - Credentials

**⚠️ IMPORTANT:**
- Never commit `.env` or credential files
- Use environment variables or managed secrets
- For production, use GCP Identity and Access Management (IAM)
- Credentials are automatically loaded from `GOOGLE_APPLICATION_CREDENTIALS`

## 🔧 Autenticación con Google Cloud

```bash
gcloud auth login
gcloud config set project TU_PROJECT_ID
# Configurar credenciales para la aplicación
gcloud auth application-default login
```

## 🚀 Uso

Ejecutar el pipeline completo:
```bash
python main.py
```

### Output esperado:
```
✓ BigQuery client initialized
✓ Project ID: tu-proyecto-gcp
✓ Extracting Iowa Liquor Sales data from BigQuery...
✓ Extracting Iowa Census data from Data Portal...
✓ Cleaning data...

--- TRANSFORMATION ---
✓ Transformed country_sales_summary_df created with X rows
✓ Transformed store_and_product_analysis_df created with Y rows
✓ Transformed price_inflation_tracker created with Z rows

Validating: Liquor Sales Raw Data
  ✓ NULL_VALUES: No null values found
  ✓ NEGATIVE_VALUES: No negative values in numerical columns
  ✓ DUPLICATES: No duplicate records found
  ✓ EMPTY_TABLE: Table has N rows
  Summary: {...}
```

## 📡 Fuentes de Datos

### BigQuery Public Data
- **Dataset**: `bigquery-public-data.iowa_liquor_sales.sales`
- **Campos extraídos**:
  - `invoice_and_item_number`: ID único de transacción
  - `date`: Fecha de venta
  - `county`: Condado
  - `store_name`: Nombre de tienda
  - `category_name`: Categoría de producto
  - `volume_sold_liters`: Volumen en litros
  - `volume_sold_gallons`: Volumen en galones
  - `sale_dollars`: Monto de venta en dólares
  - `bottles_sold`: Cantidad de botellas
- **Filtro**: Últimos 3 años fiscales
- **Límite**: 100,000 registros

### Iowa Data Portal API
- **URL**: `https://data.iowa.gov/api/dataset-download?path=datasets%2F707%2Frows.json`
- **Datos**: Población por condado y año
- **Campos**: `calendar_year`, `geographic_name`, `population`

## 🔍 Procesos de Limpieza

### Datos de Ventas de Licor
1. Capitalización de nombres de condado
2. Extracción de año y mes como campos enteros (int32)
3. Eliminación de registros inválidos

### Datos de Censo
1. Renombramiento de columnas (`calendar_year` → `year`, `geographic_name` → `county`)
2. Normalización de nombres de condado (eliminación de " County")
3. Capitalización de nombres
4. Conversión de año a int32

## 🛠 Estructura del Código

### Funciones Principales

| Función | Descripción |
|---------|-------------|
| `get_bigquery_client()` | Inicializa cliente de BigQuery |
| `extract_liquor_sales(client)` | Extrae datos de ventas desde BigQuery |
| `extract_census_data()` | Extrae datos de censo desde Iowa Data Portal |
| `clean_data(liquor_df, census_df)` | Limpia y normaliza ambos datasets |
| `transform_data(liquor_df, census_df)` | Crea las 3 tablas de análisis |
| `validate_table_quality(df, table_name)` | Valida calidad de datos |

## 📝 Ejemplos de Uso Avanzado

### Filtrar por tienda específica
```python
from main import store_and_product_analysis_df

# Obtener ventas de una tienda específica en un periodo
tienda_filter = store_and_product_analysis_df[
    (store_and_product_analysis_df["year"] == 2024) & 
    (store_and_product_analysis_df["month"] == 10) &
    (store_and_product_analysis_df["store_name"] == 'HY-VEE #3')
]
print(tienda_filter)
```

### Analizar precios por categoría
```python
# Obtener top 10 categorías más caras
top_prices = price_inflation_tracker.nlargest(10, 'average_price_per_liter')
print(top_prices[['category_name', 'average_price_per_liter']])
```

## ⚠️ Notas Importantes

- El pipeline ordena los datos por `date, county, store_name, category_name` en BigQuery para garantizar consistencia entre ejecuciones
- Los valores negativos en `bottles_sold` y `sale_dollars` pueden indicar devoluciones o ajustes en los datos originales
- El pipeline requiere conexión a internet para acceder a BigQuery y la API del Iowa Data Portal
- Las credenciales de GCP deben tener permisos de lectura en `bigquery-public-data`

## 🐛 Solución de Problemas

### Error: "GCP_PROJECT_ID not set"
```bash
# Verificar que .env existe y contiene GCP_PROJECT_ID
cat .env
```

### Error: "Authentication failed"
```bash
# Re-autenticar con Google Cloud
gcloud auth application-default login
```

### Error: "Connection timeout"
- Verificar conexión a internet
- Verificar que BigQuery esté disponible
- Verificar que la API del Iowa Data Portal sea accesible

## 📄 Licencia

Este proyecto es parte del desafío técnico de Iowa Liquor Sales Analytics.

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
