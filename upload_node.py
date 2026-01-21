import boto3
import os
import sys
from botocore.exceptions import ClientError

# --- CONFIGURATION ---
# 🔴 PLEASE FILL THESE IN AGAIN - DOUBLE CHECK FOR SPACES 🔴
ACCESS_KEY = "user_37nhR3****" 
SECRET_KEY = "FILL_ME_IN"

# RunPod Config
ENDPOINT = "https://s3api-eu-cz-1.runpod.io"
VOLUME_ID = "7xsznkj3l9" 
REGION = "eu-cz-1"

# Paths
LOCAL_NODE_PATH = os.path.join(os.getcwd(), "ComfyUI-GGUF")
REMOTE_NODE_PATH = "custom_nodes/ComfyUI-GGUF"

def upload_file(client, local, remote):
    try:
        print(f"Uploading {os.path.basename(local)} -> {remote} ... ", end="")
        client.upload_file(local, VOLUME_ID, remote)
        print("✅ OK")
        return True
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print(f"--- DEBUG UPLOAD ---")
    print(f"Endpoint: {ENDPOINT}")
    print(f"Region: {REGION}")
    print(f"Bucket: {VOLUME_ID}")
    print(f"Access Key: {ACCESS_KEY[:5]}...{ACCESS_KEY[-3:] if len(ACCESS_KEY)>5 else ''}")
    
    if "FILL_ME_IN" in SECRET_KEY or "*" in ACCESS_KEY:
        print("\n❌ STOP: You haven't replaced the keys in the script yet!")
        print("Please edit this file (upload_node.py) and paste your real keys.")
        sys.exit(1)

    s3 = boto3.client(
        's3',
        endpoint_url=ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION,
        config=boto3.session.Config(signature_version='s3v4')
    )

    # 1. TEST CONNECTION
    print("\n1️⃣ Testing connection...")
    try:
        s3.list_objects_v2(Bucket=VOLUME_ID, MaxKeys=1)
        print("✅ Connection Successful!")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("Check your Access Key and Secret Key carefully.")
        sys.exit(1)

    # 2. UPLOAD
    print("\n2️⃣ Starting Upload...")
    if not os.path.exists(LOCAL_NODE_PATH):
        print(f"❌ Local path not found: {LOCAL_NODE_PATH}")
        sys.exit(1)

    success_count = 0
    fail_count = 0

    for root, dirs, files in os.walk(LOCAL_NODE_PATH):
        for file in files:
            if ".git" in root.split(os.sep): continue
            
            local_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_path, LOCAL_NODE_PATH)
            remote_path = f"{REMOTE_NODE_PATH}/{rel_path}".replace("\\", "/")
            
            if upload_file(s3, local_path, remote_path):
                success_count += 1
            else:
                fail_count += 1

    print(f"\nSummary: {success_count} succeeded, {fail_count} failed.")
