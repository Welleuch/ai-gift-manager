import boto3
import os

# --- RUNPOD CONFIGURATION ---
ACCESS_KEY = "user_37nhR3C74zwd" 
SECRET_KEY = "REPLACE_WITH_YOUR_SECRET"
ENDPOINT = "https://s3api-eu-cz-1.runpod.io"
VOLUME_ID = "7xsznkj3l9" 
REGION = "eu-cz-1"

# --- THE CONFIGURATION CONTENT ---
# Based on your s3_shell.py output:
# Volume Root
#   ├── custom_nodes/
#   └── models/
#       ├── checkpoints/
#       ├── unet/
#       ├── ...

yaml_content = """comfyui:
    base_path: /runpod-volume
    custom_nodes: custom_nodes
    checkpoints: models/checkpoints
    unet: models/unet
    loras: models/loras
    vae: models/vae
    clip: models/clip
    
    # Mapping other folder types found in your tree
    diffusers: models/diffusion_
    text_encoders: models/text_encoders
"""

# Save locally
with open("extra_paths.yaml", "w") as f:
    f.write(yaml_content)

print("📄 Generated extra_paths.yaml based on your volume structure.")

# Upload to Volume
s3 = boto3.client(
    's3',
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION,
    config=boto3.session.Config(signature_version='s3v4')
)

try:
    print(f"☁️  Uploading to {VOLUME_ID}...")
    s3.upload_file("extra_paths.yaml", VOLUME_ID, "extra_paths.yaml")
    print("✅ Upload Successful!")
    print("\n---------------------------------------------------")
    print("FINAL STEP: Go to RunPod Console -> Edit Endpoint")
    print("Add this Environment Variable:")
    print("Key:   CLI_ARGS")
    print("Value: --extra-model-paths-config /runpod-volume/extra_paths.yaml")
    print("---------------------------------------------------")
except Exception as e:
    print(f"❌ Upload Failed: {e}")
