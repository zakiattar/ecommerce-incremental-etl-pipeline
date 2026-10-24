import os
import pandas as pd
import boto3

from io import StringIO
from pathlib import Path
from dotenv import load_dotenv


# STEP 1: PROJECT PATH
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# STEP 2: LOAD ENVIRONMENT VARIABLES
load_dotenv(BASE_DIR / ".env")

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET")


# STEP 3: VALIDATE CONFIGURATION
if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
    raise ValueError("AWS credentials missing. Check your .env file.")

if not S3_BUCKET:
    raise ValueError("S3 bucket name missing. Check your .env file.")


# STEP 4: READ CSV FILES INTO PANDAS DATAFRAMES
customer_df = pd.read_csv(DATA_DIR / "customer.csv")
orders_df = pd.read_csv(DATA_DIR / "orders.csv")
product_df = pd.read_csv(DATA_DIR / "product.csv")


# STEP 5: DISPLAY DATA
print("CUSTOMER DATA")
print(customer_df.head())
print("Customer shape:", customer_df.shape)

print("\nORDERS DATA")
print(orders_df.head())
print("Orders shape:", orders_df.shape)

print("\nPRODUCT DATA")
print(product_df.head())
print("Product shape:", product_df.shape)


# STEP 6: CREATE S3 CLIENT
s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)


# STEP 7: UPLOAD DATAFRAMES TO S3
datasets = {
    "customer.csv": customer_df,
    "orders.csv": orders_df,
    "product.csv": product_df
}

for filename, dataframe in datasets.items():
    csv_buffer = StringIO()
    dataframe.to_csv(csv_buffer, index=False)

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=f"raw/{filename}",
        Body=csv_buffer.getvalue().encode("utf-8"),
        ContentType="text/csv"
    )

    print(f"SUCCESS: {filename} uploaded to S3")


# STEP 8: PIPELINE COMPLETED
print("\nE-COMMERCE INGESTION PIPELINE COMPLETED")
print(f"S3 Bucket: {S3_BUCKET}")
print(f"AWS Region: {AWS_REGION}")