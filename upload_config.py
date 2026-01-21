import boto3
import os

# --- CONFIGURATION ---
ACCESS_KEY = "user_37nhR3C74zwd" # REPLACE WITH YOUR KEY IF NEEDED
SECRET_KEY = "REPLACE_WITH_YOUR_SECRET"
ENDPOINT = "https://s3api-eu-cz-1.runpod.io"
VOLUME_ID = "7xsznkj3l9" 
REGION = "eu-cz-1"

# Content of the config file
yaml_content = """comfyui:
    custom_nodes: /runpod-volume/custom_nodes
"""

# Save locally first
local_file = "extra_paths.yaml"
with open(local_file, "w") as f:
    f.write(yaml_content)

print(f"📄 Created {local_file}")

# Upload to RunPod Volume
s3 = boto3.client(
    's3',
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION,
    config=boto3.session.Config(signature_version='s3v4')
)

try:
    print(f"☁️  Uploading to volume root...")
    s3.upload_file(local_file, VOLUME_ID, "extra_paths.yaml")
    print("✅ Upload Successful!")
    print("NEXT STEP: Add this Environment Variable to your RunPod Endpoint:")
    print("Key:   CLI_ARGS")
    print("Value: --extra-model-paths-config /runpod-volume/extra_paths.yaml")
except Exception as e:
    print(f"❌ Upload Failed: {e}")
