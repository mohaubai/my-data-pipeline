import boto3
import pandas as pd
from io import StringIO

def process_data():
    csv_data = """
    id, name, age, city
    1,Alice, 30, New york
    2,Bob, 25, Los Angeles
    3,Charlie, 35, Chicago
    4,Diana, 28, Houston
    5,Eve, 32, Phoenix
    """
    
    df = pd.read_csv(StringIO(csv_data))
    df.columns = df.columns.str.strip()
    df['age_group'] = df['age'].apply(lambda x: 'young' if x < 30 else 'adult')

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    # s3 = boto3.client('s3')
    # bucket_name = 'my-data-lab-august-2026-ub'  # <-- You will change this
    # s3.put_object(
    #     Bucket=bucket_name,
    #     Key='clean/new_output.csv',
    #     Body=csv_buffer.getvalue()
    # )

    print(f"Uploaded {len(df)} rows to s3://{bucket_name}/clean/new_output.csv")
    print(df)

if __name__=="__main__":
    process_data()