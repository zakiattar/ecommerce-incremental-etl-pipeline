# E-commerce Incremental ETL Pipeline

## Project Overview

This project implements an incremental ETL pipeline for e-commerce data using Python, Pandas, PySpark, and AWS services.

The pipeline extracts incremental records using timestamp-based filtering, stores data in Amazon S3, transforms the data using AWS Glue, and queries the processed data using Amazon Athena.

## Technologies Used

- Python
- Pandas
- NumPy
- PySpark
- Amazon S3
- AWS Glue
- Amazon Athena
- Apache Airflow
- Docker
- SQL
- Git and GitHub

## Project Architecture

```text
E-commerce CSV Files
        |
        v
Python and Pandas
        |
        v
Incremental Data Extraction
        |
        v
Amazon S3
        |
        v
AWS Glue and PySpark
        |
        v
Processed Data in S3
        |
        v
Amazon Athena
        |
        v
SQL Queries
```

## Dataset

The project uses three CSV datasets:

- `customer.csv`
- `orders.csv`
- `product.csv`

## Incremental Data Loading

The pipeline uses timestamp-based filtering and a watermark to identify records for incremental processing.

The watermark advances only after a successful S3 upload, helping reduce the risk of skipping records when an upload fails.

## Data Transformation

AWS Glue and PySpark are used to:

- Read incremental order data from Amazon S3.
- Remove duplicate records using `order_id`.
- Trim whitespace from order status values.
- Write processed data back to Amazon S3.

## Data Validation

Amazon Athena is used to query the processed data using SQL.

During one test run, the incremental order dataset contained 454 records, and Athena returned a count of 454 records.

## Project Structure

```text
ecommerce_ETL/
├── .gitignore
├── README.md
├── requirements.txt
├── data/
├── sql/
│   └── validate_orders.sql
└── src/
    ├── increment_load.py
    └── read_csv.py
```

## Security

- AWS credentials are stored outside the source code.
- The `.env` file is excluded using `.gitignore`.
- Credentials and sensitive customer data should never be committed to a public repository.

## Future Improvements

- Add automated data quality checks.
- Improve handling of late-arriving records.
- Add pipeline monitoring and notifications.
- Integrate Amazon Redshift.
- Improve Airflow orchestration and automated testing.

## Author

Data Engineering Project