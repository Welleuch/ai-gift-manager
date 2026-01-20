import boto3
import os
import sys
from tqdm import tqdm

# --- CONFIGURATION ---
ACCESS_KEY = "user_37nhR3C74VgEEdVcZv6sCNwoOnK"
SECRET_KEY = "REPLACE_WITH_YOUR_SECRET" # <-- PUT YOUR SECRET KEY HERE
ENDPOINT = "https://s3api-eu-cz-1.runpod.io"
VOLUME_ID = "7xsznkj3l9"
REGION = "eu-cz-1"

# The new model we are adding
# Link: https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors
LOCAL_FILE_PATH = r"C:\Users\Administrator\Downloads\z_image_turbo_bf16.safetensors"
REMOTE_KEY = "models/diffusion_models/z_image_turbo_bf16.safetensors"

s3 = boto3.client(
    's3',
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION,
    config=boto3.session.Config(signature_version='s3v4')
)

def upload_file(local_path, remote_key):
    if not os.path.exists(local_path):
        print(f"❌ Error: Local file not found at {local_path}")
        print("Please download it from: https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors")
        return

    file_size = os.path.getsize(local_path)
    print(f"🚀 Uploading {os.path.basename(local_path)} ({file_size/1024/1024/1024:.2f} GB) to {remote_key}...")
    
    with tqdm(total=file_size, unit='B', unit_scale=True, desc="Uploading") as pbar:
        try:
            s3.upload_file(
                Filename=local_path,
                Bucket=VOLUME_ID,
                Key=remote_key,
                Callback=lambda bytes_transferred: pbar.update(bytes_transferred)
            )
            print("\n✅ Upload Complete!")
        except Exception as e:
            print(f"\n❌ Upload Failed: {e}")

if __name__ == "__main__":
    upload_file(LOCAL_FILE_PATH, REMOTE_KEY)
