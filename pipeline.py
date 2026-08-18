import logging
import sys
from io import StringIO

import boto3
import pandas as pd
from botocore.exceptions import BotoCoreError, ClientError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def process_data():
    csv_data = """id,name,age,city
1,Alice,30,New York
2,Bob,25,Los Angeles
3,Charlie,35,Chicago
4,Diana,28,Houston
5,Eve,32,Phoenix"""

    df = pd.read_csv(StringIO(csv_data))
    df['age_group'] = df['age'].apply(lambda x: 'young' if x < 30 else 'adult')

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    s3 = boto3.client('s3')
    bucket_name = 'my-data-lab-2026-august-ub'  # <-- YOUR EXACT BUCKET NAME
    key = 'clean/output.csv'  # <-- This creates the file inside the clean/ folder
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=csv_buffer.getvalue()
        )
    except (ClientError, BotoCoreError):
        logger.exception("Failed to upload to s3://%s/%s", bucket_name, key)
        raise

    logger.info("✅ Uploaded %d rows to s3://%s/%s", len(df), bucket_name, key)
    print(df)


if __name__ == "__main__":
    try:
        process_data()
    except Exception:
        logger.exception("Pipeline failed")
        sys.exit(1)
