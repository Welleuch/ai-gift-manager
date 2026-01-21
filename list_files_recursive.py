import boto3
import os

ACCESS_KEY = "user_37nhR3C74zwd" # REPLACE WITH YOUR KEY 
SECRET_KEY = "REPLACE_WITH_YOUR_SECRET"
ENDPOINT = "https://s3api-eu-cz-1.runpod.io"
VOLUME_ID = "7xsznkj3l9" 
REGION = "eu-cz-1"

s3 = boto3.client(
    's3',
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION,
    config=boto3.session.Config(signature_version='s3v4')
)

print(f"📂 Listing ALL files in Volume: {VOLUME_ID}...\n")

try:
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=VOLUME_ID)

    count = 0
    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                print(f"  {obj['Key']}")
                count += 1
                if count > 50:
                    print("... (truncating output) ...")
                    break
        if count > 50: break

    if count == 0:
        print("❌ Volume is empty.")

except Exception as e:
    print(f"❌ Error: {e}")
