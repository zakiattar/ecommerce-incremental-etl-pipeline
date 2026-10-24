# E-commerce Incremental ETL Pipeline

## Project Overview

The E-commerce Incremental ETL Pipeline is a cloud-based data engineering project designed to process e-commerce data efficiently using incremental data loading.

The pipeline identifies new records using timestamp-based filtering and processes incremental data instead of repeatedly processing the entire dataset.

This project uses Python, Pandas, PySpark, Amazon S3, AWS Glue, Amazon Athena, and Apache Airflow to build an incremental data processing workflow.

## Project Objectives

- Build an incremental ETL pipeline for e-commerce data.
- Extract data from CSV files using Python and Pandas.
- Implement timestamp-based incremental data loading.
- Store raw and incremental data in Amazon S3.
- Transform data using PySpark and AWS Glue.
- Query processed data using Amazon Athena.
- Organize pipeline execution using Apache Airflow.