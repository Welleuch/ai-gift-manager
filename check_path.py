import boto3
from botocore.exceptions import ClientError

ACCESS_KEY = "user_37nhR3C74zwd"
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

print("🔍 Checking specific paths...")

paths_to_check = [
    "custom_nodes/ComfyUI-GGUF/nodes.py",
    "ComfyUI-GGUF/nodes.py",
    "ComfyUI/custom_nodes/ComfyUI-GGUF/nodes.py",
    "nodes.py"
]

found = False
for path in paths_to_check:
    try:
        s3.head_object(Bucket=VOLUME_ID, Key=path)
        print(f"✅ FOUND: {path}")
        found = True
    except ClientError:
        print(f"❌ Not found: {path}")

if not found:
    print("\n⚠️  Could not find nodes.py in any expected location!")
else:
    print("\n✨ At least one valid path exists.")
