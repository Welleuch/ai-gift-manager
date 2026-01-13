import runpod
import os
import requests
import json
import base64
import subprocess
import re
import random
from pathlib import Path
import boto3

# --- R2 SETUP ---
def get_r2_client():
    return boto3.client(
        service_name='s3',
        endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
        aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
        region_name="auto"
    )

def upload_data_to_r2(data, file_name, is_base64=True):
    try:
        client = get_r2_client()
        bucket = os.getenv("R2_BUCKET_NAME")
        content_type = "image/png" if file_name.endswith(".png") else "model/gltf-binary"
        if file_name.endswith(".gcode"): content_type = "text/x.gcode"

        body = base64.b64decode(data) if is_base64 else data
        client.put_object(Bucket=bucket, Key=file_name, Body=body, ContentType=content_type)
        return f"{os.getenv('R2_PUBLIC_URL')}/{file_name}"
    except Exception as e:
        print(f"R2 Error: {e}")
        return None

# --- GPU WORKER CALLER ---
def call_gpu_artist(workflow):
    url = f"https://api.runpod.ai/v2/{os.getenv('GPU_ENDPOINT_ID')}/runsync"
    headers = {"Authorization": f"Bearer {os.getenv('RUNPOD_API_KEY')}"}
    response = requests.post(url, json={"input": {"workflow": workflow}}, headers=headers, timeout=300)
    return response.json()

# --- THE HANDLER ---
def handler(job):
    try:
        job_input = job['input']
        task_type = job_input.get("type")

        # A. CHAT
        if task_type == "CHAT":
            return {
                "response": "Designing your 3D gift now...",
                "visual_prompt": job_input.get("message")
            }

        # B. IMAGE GENERATION
        if task_type == "GEN_IMAGE":
            with open("/workflows/stage1_image.json", "r") as f:
                workflow = json.load(f)
            
            # Inject your perfect prompt template
            prompt = f"Product designer figurine: {job_input.get('visual_prompt')}. Style: matte gray PLA, chunky solid geometry, white background."
            workflow["34:27"]["inputs"]["text"] = prompt
            workflow["34:3"]["inputs"]["seed"] = random.randint(1, 10**14)

            res = call_gpu_artist(workflow)
            # The xHaileab worker returns base64 in 'message'
            b64_data = res['output']['message']
            url = upload_data_to_r2(b64_data, f"img_{job['id']}.png")
            return {"images": [url]}

        # C. 3D GENERATION
        if task_type == "GEN_3D":
            with open("/workflows/stage2_3d_final.json", "r") as f:
                workflow = json.load(f)
            
            # Note: Stage 2 worker handles image loading from URL
            workflow["1"]["inputs"]["image"] = job_input.get("image_url")
            
            res = call_gpu_artist(workflow)
            b64_data = res['output']['message']
            url = upload_data_to_r2(b64_data, f"model_{job['id']}.glb")
            return {"images": [url]}

        # D. SLICING
        if task_type == "SLICE":
            stl_b64 = job_input.get("stl_data")
            temp_stl = "/tmp/input.stl"
            output_gcode = "/tmp/output.gcode"
            
            with open(temp_stl, "wb") as f: f.write(base64.b64decode(stl_b64))
            
            subprocess.run(["/usr/bin/prusaslicer", "--export-gcode", "--center", "100,100", "--ensure-on-bed", "--load", "/config.ini", "--output", output_gcode, temp_stl], check=True)
            
            content = Path(output_gcode).read_text()
            vol = re.search(r"used \[cm3\]\s*=\s*([\d\.]+)", content)
            weight = float(vol.group(1)) * 1.24 if vol else 10.0
            
            url = upload_data_to_r2(Path(output_gcode).read_bytes(), f"print_{job['id']}.gcode", is_base64=False)
            return {"status": "success", "gcode_url": url, "weight": round(weight,1), "price": round((weight*0.05)+12, 2), "print_time": "2h 45m"}

    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

runpod.serverless.start({"handler": handler})