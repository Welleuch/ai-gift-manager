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

# --- 1. CLOUDFLARE R2 SETUP ---
def get_r2_client():
    return boto3.client(
        service_name='s3',
        endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
        aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
        region_name="auto"
    )

def upload_to_r2(local_path, file_name):
    try:
        client = get_r2_client()
        bucket = os.getenv("R2_BUCKET_NAME")
        
        # Determine content type
        if file_name.endswith(".png"): content_type = "image/png"
        elif file_name.endswith(".glb"): content_type = "model/gltf-binary"
        elif file_name.endswith(".gcode"): content_type = "text/x.gcode"
        else: content_type = "application/octet-stream"

        client.upload_file(local_path, bucket, file_name, ExtraArgs={'ContentType': content_type})
        return f"{os.getenv('R2_PUBLIC_URL')}/{file_name}"
    except Exception as e:
        print(f"R2 Error: {e}")
        return None

# --- 2. GPU ARTIST FORWARDER ---
def call_gpu_artist(workflow):
    """Sends the ComfyUI JSON to your GPU Serverless Endpoint"""
    endpoint_id = os.getenv("GPU_ENDPOINT_ID")
    api_key = os.getenv("RUNPOD_API_KEY")
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}/runsync"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    payload = {"input": {"workflow": workflow}}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=300)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- 3. THE HANDLER (THE BRAIN) ---
def handler(job):
    job_input = job['input']
    task_type = job_input.get("type") # "CHAT", "GEN_IMAGE", "GEN_3D", or "SLICE"

    # A. CHAT LOGIC (Formatting the prompt)
    if task_type == "CHAT":
        user_input = job_input.get("message")
        return {
            "response": "I'm applying 3D-printing design rules to your idea...",
            "visual_prompt": user_input 
        }

    # B. GENERATION LOGIC (Forwarding to GPU)
    if task_type in ["GEN_IMAGE", "GEN_3D"]:
        workflow = job_input.get("workflow")
        # Call the GPU worker
        gpu_result = call_gpu_artist(workflow)
        
        # The xHaileab worker returns images as Base64 in the 'message' field
        if "output" in gpu_result and "message" in gpu_result["output"]:
            # Logic to handle base64 strings and upload to R2
            # (Simplified for now: return the GPU result)
            return gpu_result["output"]
        return {"error": "GPU worker failed"}

    # C. SLICING LOGIC (Running PrusaSlicer)
    if task_type == "SLICE":
        try:
            # 1. Decode STL from input (Frontend will send it as Base64)
            stl_base64 = job_input.get("stl_data")
            temp_stl = Path("/tmp/gift.stl")
            with open(temp_stl, "wb") as f:
                f.write(base64.b64decode(stl_base64))

            # 2. Run Slicer
            output_gcode = "/tmp/final.gcode"
            config_path = "/config.ini" # From our Docker image
            
            command = [
                "/usr/bin/prusaslicer", "--export-gcode", 
                "--center", "100,100", "--ensure-on-bed",
                "--load", config_path, "--output", output_gcode, str(temp_stl)
            ]
            subprocess.run(command, check=True)

            # 3. Parse Metadata
            content = Path(output_gcode).read_text()
            vol = re.search(r"used \[cm3\]\s*=\s*([\d\.]+)", content)
            weight = float(vol.group(1)) * 1.24 if vol else 10.0
            
            # 4. Upload G-Code to R2
            gcode_url = upload_to_r2(output_gcode, f"print_{job['id']}.gcode")

            return {
                "status": "success",
                "gcode_url": gcode_url,
                "weight": round(weight, 1),
                "price": round((weight * 0.05) + 12, 2)
            }
        except Exception as e:
            return {"error": str(e)}

    return {"error": "Invalid task type"}

# Start the RunPod Serverless worker
runpod.serverless.start({"handler": handler})