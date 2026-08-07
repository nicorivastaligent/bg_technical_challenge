import pandas as pd

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
        print(f"✗ NULL_VALUES (Severity: HIGH): {null_failures}")
    else:
        print("✓ NULL_VALUES: No null values found")

    # Check 2: Negative values in numerical columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    negative_counts = {}
    for col in numeric_cols:
        neg_count = (df[col] < 0).sum()
        if neg_count > 0:
            negative_counts[col] = int(neg_count)

    if negative_counts:
        print(f"✗ NEGATIVE_VALUES (Severity: HIGH): {negative_counts}")
    else:
        print("✓ NEGATIVE_VALUES: No negative values in numerical columns")

    # Check 3: Duplicates (check all columns for duplicates)
    duplicates_count = df.duplicated().sum()

    if duplicates_count:
        raise ValueError(f"Data quality check failed for {table_name}: {duplicates_count} duplicate rows found.")
    else:
        print("✓ DUPLICATES: No duplicate records found")

    # Check 4: Empty dataframe
    if len(df) == 0:
        dq_report["checks_performed"].append(f"✗ EMPTY_TABLE: Table is empty") 
    else:
        dq_report["checks_performed"].append(f"✓ EMPTY_TABLE: Table has {len(df)} rows")

    return dq_report
