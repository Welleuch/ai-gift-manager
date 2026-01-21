# clean_volume_bulk.py
# --------------------------------------------------------------
# Delete everything that is NOT needed for:
#   • PrusaSlicer (kept in the `slicer/` folder)
#   • Your Z‑Image‑Turbo safetensors model
#   • The Hunyuan‑3D checkpoint
#   • The Qwen text‑encoder and VAE
# --------------------------------------------------------------
import boto3
import sys
from botocore.exceptions import ClientError
# --------------------------------------------------------------
# 1️⃣  Fill in your RunPod credentials (same ones you used in upload_node.py)
# --------------------------------------------------------------
ACCESS_KEY = "user_37nhR3C74VgEEdVcZv6sCNwoOnK"
SECRET_KEY = "rps_6K36OQQNGSFC2JJXV2Q7VKYJ809TDNLJV591XCXR1djhh7"   # <-- put the real secret here
ENDPOINT   = "https://s3api-eu-cz-1.runpod.io"
VOLUME_ID  = "7xsznkj3l9"
REGION     = "eu-cz-1"
# --------------------------------------------------------------
# 2️⃣  Prefixes / exact objects that must be removed
# --------------------------------------------------------------
# NOTE: each entry ending with '/' is a *folder* (all objects that start
# with that string will be deleted).  Plain strings are single files.
PREFIXES_TO_DELETE = [
    # ── Large duplicate / unused diffusion files
    "models/diffusion_/hunyuan3d-dit-v2-0-fp16.safetensors",
    "models/diffusion_/model.fp16.safetensors",
    # ── Old GGUF version of Z‑Image (both copies)
    "models/diffusion_/z_image_turbo-Q8_0.gguf",
    "models/unet/z_image_turbo-Q8_0.gguf",
    # ── Entire runpod‑slim runtime (not needed for the GPU worker)
    "runpod-slim/",
    # ── Optional: BiRefNet up‑scaler checkpoints (≈ 3 GB)
    # Uncomment if you ever need them.
    # "models/BiRefNet/",
    # ── Hidden marker folders (they contain only tiny metadata files)
    ".cache/",
    ".ipynb_checkpoints/",
    ".s3compat_uploads/",
    # ── Demo STL (tiny, optional)
    "temp_gift.stl",
]
# --------------------------------------------------------------
# 3️⃣  Build the S3 client (path‑style addressing works best with RunPod)
# --------------------------------------------------------------
s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION,
    config=boto3.session.Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"}   # important for RunPod
    )
)
def delete_prefix(prefix: str) -> int:
    """
    Delete every object that starts with `prefix`.
    Returns the number of objects removed.
    """
    print(f"\n🗑️  Deleting prefix: {prefix}")
    continuation = None
    removed = 0
    while True:
        params = {
            "Bucket": VOLUME_ID,
            "Prefix": prefix,
            "MaxKeys": 1000,          # max objects per request
        }
        if continuation:
            params["ContinuationToken"] = continuation
        resp = s3.list_objects_v2(**params)
        # No more objects under this prefix
        if "Contents" not in resp:
            break
        for obj in resp["Contents"]:
            key = obj["Key"]
            try:
                s3.delete_object(Bucket=VOLUME_ID, Key=key)
                removed += 1
                # In‑line progress indicator
                sys.stdout.write(f"\r   → Deleted {removed} objects")
                sys.stdout.flush()
            except ClientError as e:
                print(f"\n❌ Failed to delete {key}: {e}")
        # Continue if there are more pages
        if resp.get("IsTruncated"):
            continuation = resp.get("NextContinuationToken")
        else:
            break
    print(f"\n✅ Finished {prefix} ({removed} objects removed)")
    return removed
def main():
    total_removed = 0
    for p in PREFIXES_TO_DELETE:
        total_removed += delete_prefix(p)
    print("\n🎉 Bulk‑clean complete!")
    print(f"Total objects removed: {total_removed}")
    print("\nNow run `python s3_shell.py` and issue `du` – you should see the usage well under the 50 GB quota.")
    print("After that you can re‑run [upload_new_model.py](cci:7://file:///c:/Users/Administrator/Downloads/ai-gift-manager/upload_new_model.py:0:0-0:0) if you need to push any additional files.")
    print("\n⚠️  IMPORTANT: The `slicer/` folder was **not** touched – your PrusaSlicer installation remains intact.")
if __name__ == "__main__":
    main()