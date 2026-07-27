# Task 2: Data Quality & Performance

## 2.1 Data Quality
The data pipeline implements automated data quality checks, validating criteria such as null values, negative values in numeric columns, duplicate rows, and empty tables. When evaluating the checks, the code implements an error handling mechanism that logs the results and assesses the severity of any failures. The pipeline only stops execution (raises an exception) when a data quality error is categorized as CRITICAL (for example, when duplicate records are detected). For non-critical issues, it reports the failure but allows the pipeline to continue.

## 2.2 Performance
If this dataset had 10 Terabytes I would implement the following strategies:

* **Table Structuring & Normalization:** I would restructure the tables into First Normal Form (1NF), Second Normal Form (2NF), and Third Normal Form (3NF). This normalization process ensures that data redundancy is avoided, storage is optimized, and data integrity is maintained across the warehouse.
* **Batch Processing:** To handle the massive scale of the data efficiently, the ingestion process would be executed in batches partitioned or chunked by the `invoice_and_item_number` field. 
* **Incremental Loading:** Instead of performing full historical loads, I would implement an incremental loading strategy. The pipeline would fetch and merge only the newest records by filtering the data using the `date` field (e.g., retrieving records where the date is greater than or equal to today). This significantly reduces the processing time and computing costs on BigQuery.
"""