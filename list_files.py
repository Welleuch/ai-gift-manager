import boto3
import os

# --- USE YOUR KEYS HERE ---
# (I've pre-filled the non-secret parts from your previous logs)
ACCESS_KEY = "user_37nhR3C74zwd" # REPLACE WITH FULL KEY
SECRET_KEY = "REPLACE_WITH_YOUR_SECRET_KEY"
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

print(f"📂 Listing folders in Volume: {VOLUME_ID}...\n")

try:
    # List top-level objects to guess structure
    response = s3.list_objects_v2(Bucket=VOLUME_ID, MaxKeys=300)
    
    if 'Contents' in response:
        # Get unique folder names (up to depth 3 for clarity)
        seen_paths = set()
        for obj in response['Contents']:
            key = obj['Key']
            # unexpected files at root?
            if "/" not in key:
                print(f"  [File] {key}")
                continue
                
            parts = key.split("/")
            # Show the first 2-3 levels of directories
            if len(parts) > 1:
                path_depth_1 = f"{parts[0]}/"
                path_depth_2 = f"{parts[0]}/{parts[1]}/" if len(parts) > 2 else ""
                
                if path_depth_1 not in seen_paths:
                    print(f"  [Dir]  {path_depth_1}")
                    seen_paths.add(path_depth_1)
                
                if path_depth_2 and path_depth_2 not in seen_paths:
                    print(f"  [Dir]  {path_depth_2}")
                    seen_paths.add(path_depth_2)

    else:
        print("❌ Volume appears empty!")

except Exception as e:
    print(f"❌ Error: {e}")
