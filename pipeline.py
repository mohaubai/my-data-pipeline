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
    s3.put_object(
        Bucket=bucket_name,
        Key='clean/output.csv',  # <-- This creates the file inside the clean/ folder
        Body=csv_buffer.getvalue()
    )
    
    print(f"✅ Uploaded {len(df)} rows to s3://{bucket_name}/clean/output.csv")
    print(df)