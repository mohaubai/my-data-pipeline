from io import StringIO

import boto3
import pandas as pd

BUCKET_NAME = 'my-data-lab-2026-august-ub'
OUTPUT_KEY = 'clean/output.csv'

RAW_CSV = """id,name,age,city
1,Alice,30,New York
2,Bob,25,Los Angeles
3,Charlie,35,Chicago
4,Diana,28,Houston
5,Eve,32,Phoenix"""


def age_group(age):
    return 'young' if age < 30 else 'adult'


def transform(df):
    df = df.copy()
    df.columns = [column.strip() for column in df.columns]
    df['age_group'] = df['age'].apply(age_group)
    return df


def upload(df, bucket_name=BUCKET_NAME, key=OUTPUT_KEY):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    s3 = boto3.client('s3')
    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=csv_buffer.getvalue()
    )


def process_data(raw_csv=RAW_CSV, bucket_name=BUCKET_NAME, key=OUTPUT_KEY):
    df = transform(pd.read_csv(StringIO(raw_csv)))
    upload(df, bucket_name=bucket_name, key=key)

    print(f"Uploaded {len(df)} rows to s3://{bucket_name}/{key}")
    print(df)
    return df


if __name__ == '__main__':
    process_data()
