

import os
import json
import boto3
import pandas as pd

from io import StringIO
from pathlib import Path
from dotenv import load_dotenv


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET")

ORDERS_FILE = BASE_DIR / "data" / "orders.csv"
WATERMARK_FILE = BASE_DIR / "data" / "orders_watermark.json"

S3_KEY = "incremental/orders/orders_incremental.csv"


# --------------------------------------------------
# 2. VALIDATE CONFIGURATION
# --------------------------------------------------

if not S3_BUCKET:
    raise ValueError(
        "S3_BUCKET .env file mein configured nahi hai."
    )

if not ORDERS_FILE.exists():
    raise FileNotFoundError(
        f"Orders CSV file nahi mili: {ORDERS_FILE}"
    )


# --------------------------------------------------
# 3. CREATE S3 CLIENT
# --------------------------------------------------

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION
)


# --------------------------------------------------
# 4. READ ORDERS CSV
# --------------------------------------------------

orders_df = pd.read_csv(
    ORDERS_FILE,
    sep="\t"
)

print("Total source records:", len(orders_df))


# --------------------------------------------------
# 5. VALIDATE REQUIRED COLUMN
# --------------------------------------------------

if "updated_at" not in orders_df.columns:
    raise ValueError(
        "CSV mein updated_at column nahi mila. "
        f"Available columns: {list(orders_df.columns)}"
    )


# --------------------------------------------------
# 6. CONVERT UPDATED_AT TO DATETIME
# --------------------------------------------------

orders_df["updated_at"] = pd.to_datetime(
    orders_df["updated_at"],
    format="%d-%m-%Y %H:%M",
    errors="coerce"
)

invalid_records = orders_df["updated_at"].isna().sum()

print("Invalid timestamp records:", invalid_records)

orders_df = orders_df.dropna(
    subset=["updated_at"]
).copy()

if orders_df.empty:
    print("No valid records available.")
    raise SystemExit(0)


# --------------------------------------------------
# 7. READ EXISTING WATERMARK
# --------------------------------------------------

if WATERMARK_FILE.exists():

    with open(
        WATERMARK_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        watermark = json.load(file)

    last_loaded_value = watermark.get("last_updated_at")

    if not last_loaded_value:
        raise ValueError(
            "Watermark file mein last_updated_at missing hai."
        )

    last_loaded_date = pd.to_datetime(
        last_loaded_value,
        errors="raise"
    )

else:

    # Initial watermark for the first run.
    last_loaded_date = pd.Timestamp(
        "2026-10-12 00:00:00"
    )

print("Current watermark:", last_loaded_date)


# --------------------------------------------------
# 8. FILTER INCREMENTAL RECORDS
# --------------------------------------------------

incremental_df = orders_df[
    orders_df["updated_at"] > last_loaded_date
].copy()

print("Incremental records:", len(incremental_df))


# --------------------------------------------------
# 9. STOP IF NO NEW RECORDS
# --------------------------------------------------

if incremental_df.empty:

    print("No new records found.")
    print("Nothing uploaded to S3.")

    raise SystemExit(0)


# --------------------------------------------------
# 10. FIND NEW WATERMARK
# --------------------------------------------------

new_watermark_date = incremental_df["updated_at"].max()

print(
    "Earliest incremental timestamp:",
    incremental_df["updated_at"].min()
)

print(
    "Latest incremental timestamp:",
    new_watermark_date
)


# --------------------------------------------------
# 11. CONVERT INCREMENTAL DATA TO CSV
# --------------------------------------------------

csv_buffer = StringIO()

incremental_df.to_csv(
    csv_buffer,
    index=False
)


# --------------------------------------------------
# 12. UPLOAD INCREMENTAL DATA TO S3
# --------------------------------------------------

s3.put_object(
    Bucket=S3_BUCKET,
    Key=S3_KEY,
    Body=csv_buffer.getvalue().encode("utf-8"),
    ContentType="text/csv"
)

print("S3 upload successful!")
print("Bucket:", S3_BUCKET)
print("S3 Key:", S3_KEY)


# --------------------------------------------------
# 13. UPDATE WATERMARK AFTER SUCCESSFUL UPLOAD
# --------------------------------------------------

new_watermark = {
    "last_updated_at": new_watermark_date.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
}

temp_file = WATERMARK_FILE.with_suffix(".tmp")

with open(
    temp_file,
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        new_watermark,
        file,
        indent=4
    )

temp_file.replace(WATERMARK_FILE)

print("Watermark updated:", new_watermark)


# --------------------------------------------------
# 14. PIPELINE COMPLETED
# --------------------------------------------------

print("Incremental load completed successfully!") 