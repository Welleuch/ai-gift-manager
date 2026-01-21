import runpod
from runpod.serverless import start
import os
import requests
import json
import base64
import subprocess
import re
import random
import traceback
import time
from pathlib import Path
import boto3

# --- START XVFB FOR HEADLESS PRUSASLICER ---
xvfb_process = None

def start_xvfb():
    """Start Xvfb virtual display for headless PrusaSlicer"""
    global xvfb_process
    if xvfb_process is None:
        try:
            xvfb_process = subprocess.Popen(
                ['Xvfb', ':99', '-screen', '0', '1024x768x24', '-ac'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(2)
            print("✓ Xvfb started for headless PrusaSlicer")
        except Exception as e:
            print(f"⚠️ Xvfb start failed: {e}")

# Initialize Xvfb when module loads
start_xvfb()

# --- R2 SETUP ---
def get_r2_client():
    """Create and return Cloudflare R2 client"""
    return boto3.client(
        service_name='s3',
        endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
        aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
        region_name="auto"
    )

def upload_data_to_r2(data, file_name, is_base64=True):
    """Upload file to R2 and return public URL"""
    try:...
    
        client = get_r2_client()
        bucket = os.getenv("R2_BUCKET_NAME")
        
        # Determine content type
        content_type = "image/png" if file_name.endswith(".png") else "model/gltf-binary"
        if file_name.endswith(".gcode"): 
            content_type = "text/x.gcode"

        # Decode if base64
        body = base64.b64decode(data) if is_base64 else data
        
        # Upload to R2
        client.put_object(
            Bucket=bucket, 
            Key=file_name, 
            Body=body, 
            ContentType=content_type
        )
        
        public_url = f"{os.getenv('R2_PUBLIC_URL')}/{file_name}"
        print(f"✓ Uploaded to R2: {public_url}")
        return public_url
        
    except Exception as e:
        print(f"❌ R2 Upload Error: {e}")
        return None

# --- CORRECT GPU WORKER CALLER ---
def call_gpu_artist(prompt_data, job_id, timeout=600):
    """Call the GPU endpoint for image/3D generation ASYNCHRONOUSLY"""
    api_key = os.getenv('RUNPOD_API_KEY')
    endpoint_id = os.getenv('GPU_ENDPOINT_ID')
    
    if not api_key or not endpoint_id:
        raise Exception("Missing RUNPOD_API_KEY or GPU_ENDPOINT_ID environment variables")
    
    # 1. Start the job asynchronously
    start_url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"🎨 Starting ComfyUI job on endpoint {endpoint_id}...")
    
    payload = {
        "input": {
            "workflow": prompt_data,
            "client_id": f"handler-{job_id}",
            "extra_data": {"job_id": job_id}
        }
    }
    
    print(f"📤 Sending payload to ComfyUI...")
    
    try:
        response = requests.post(start_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        job_data = response.json()
        
        if 'id' not in job_data:
            raise Exception(f"No job ID in response: {job_data}")
        
        job_id = job_data['id']
        print(f"✅ Job started with ID: {job_id}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to start job: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        raise Exception(f"Failed to start ComfyUI job: {e}")
    
    # 2. Poll for completion
    status_url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            status_response = requests.get(status_url, headers=headers, timeout=30)
            status_response.raise_for_status()
            status_data = status_response.json()
            
            print(f"📊 Job status: {status_data.get('status')}")
            
            if status_data['status'] == 'COMPLETED':
                print("✅ Job completed successfully!")
                
                # Extract output from ComfyUI response
                output = status_data.get('output', {})
                
                # ComfyUI returns image data in different formats
                if 'images' in output:
                    # Handle multiple images
                    return {"images": output['images']}
                elif 'message' in output:
                    # Handle single base64 image
                    return {"message": output['message']}
                else:
                    # Return raw output for debugging
                    print(f"📦 Raw output: {output}")
                    return output
                    
            elif status_data['status'] == 'FAILED':
                error_msg = status_data.get('error', 'Unknown error')
                print(f"❌ Job failed: {error_msg}")
                raise Exception(f"ComfyUI job failed: {error_msg}")
                
            elif status_data['status'] == 'IN_QUEUE':
                print("⏳ Job in queue, waiting...")
                
            elif status_data['status'] == 'IN_PROGRESS':
                print("🔄 Job in progress...")
                
            time.sleep(5)  # Wait 5 seconds before polling again
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Polling error: {e}")
            time.sleep(5)
    
    raise Exception(f"Job timeout after {timeout} seconds")

# --- THE MAIN HANDLER ---
def handler(job):
    """Main RunPod serverless handler"""
    try:
        job_input = job['input']
        task_type = job_input.get("type")
        job_id = job.get('id', 'unknown')
        
        print(f"📥 Received job type: {task_type}, Job ID: {job_id}")

        # ==================== A. CHAT ====================
        if task_type == "CHAT":
            return {
                "response": "Designing your 3D gift now...",
                "visual_prompt": job_input.get("message")
            }

        # ==================== B. IMAGE GENERATION ====================
        if task_type == "GEN_IMAGE":
            print("🖼️ Starting image generation...")
            
            with open("/app/workflows/stage1_image.json", "r") as f:
                workflow = json.load(f)
            
            # Inject prompt
            prompt = f"Product designer figurine: {job_input.get('visual_prompt')}. Style: matte gray PLA, chunky solid geometry, white background."
            workflow["34:27"]["inputs"]["text"] = prompt
            workflow["34:3"]["inputs"]["seed"] = random.randint(1, 10**14)

            # Call GPU worker CORRECTLY
            res = call_gpu_artist(workflow, job_id, timeout=300)
            
            # Extract base64 image from response
            if 'message' in res:
                b64_data = res['message']
            elif 'images' in res and len(res['images']) > 0:
                b64_data = res['images'][0]
            else:
                raise Exception(f"Unexpected response format: {res}")
            
            # Upload to R2
            url = upload_data_to_r2(b64_data, f"img_{job_id}.png")
            
            if not url:
                raise Exception("Failed to upload image to R2")
            
            return {"images": [url]}

        # ==================== C. 3D GENERATION ====================
        if task_type == "GEN_3D":
            print("🧊 Starting 3D generation...")
            
            with open("/app/workflows/stage2_3d_final.json", "r") as f:
                workflow = json.load(f)
            
            # Pass image URL to workflow
            workflow["1"]["inputs"]["image"] = job_input.get("image_url")
            
            # Call GPU worker
            res = call_gpu_artist(workflow, job_id, timeout=600)  # Longer timeout for 3D
            
            # Extract 3D model from response
            if 'message' in res:
                b64_data = res['message']
            elif 'images' in res and len(res['images']) > 0:
                b64_data = res['images'][0]
            else:
                raise Exception(f"Unexpected response format: {res}")
            
            # Upload to R2
            url = upload_data_to_r2(b64_data, f"model_{job_id}.glb")
            
            if not url:
                raise Exception("Failed to upload 3D model to R2")
            
            return {"images": [url]}

        # ==================== D. SLICING ====================
        if task_type == "SLICE":
            print("🔪 Starting PrusaSlicer processing...")
            
            stl_b64 = job_input.get("stl_data")
            temp_stl = "/tmp/input.stl"
            output_gcode = "/tmp/output.gcode"
            
            # Decode and save STL file
            with open(temp_stl, "wb") as f: 
                f.write(base64.b64decode(stl_b64))
            
            print(f"✓ STL saved to {temp_stl}")
            
            # Run PrusaSlicer
            slicer_cmd = [
                "prusa-slicer",
                "--export-gcode",
                "--center", "100,100",
                "--ensure-on-bed",
                "--load", "/config.ini",
                "--output", output_gcode,
                temp_stl
            ]
            
            print(f"🔧 Running: {' '.join(slicer_cmd)}")
            
            result = subprocess.run(
                slicer_cmd, 
                capture_output=True, 
                text=True
            )
            
            # Check for errors
            if result.returncode != 0:
                print(f"❌ PrusaSlicer STDERR: {result.stderr}")
                print(f"❌ PrusaSlicer STDOUT: {result.stdout}")
                raise Exception(f"PrusaSlicer failed with exit code {result.returncode}: {result.stderr}")
            
            print(f"✓ G-code generated successfully")
            
            # Parse G-code for statistics
            content = Path(output_gcode).read_text()
            vol_match = re.search(r"used \[cm3\]\s*=\s*([\d\.]+)", content)
            weight = float(vol_match.group(1)) * 1.24 if vol_match else 10.0
            
            print(f"📊 Weight: {weight}g")
            
            # Upload to R2
            url = upload_data_to_r2(
                Path(output_gcode).read_bytes(), 
                f"print_{job_id}.gcode", 
                is_base64=False
            )
            
            if not url:
                raise Exception("Failed to upload G-code to R2")
            
            return {
                "status": "success", 
                "gcode_url": url, 
                "weight": round(weight, 1), 
                "price": round((weight * 0.05) + 12, 2), 
                "print_time": "2h 45m"
            }
        
        # Unknown task type
        return {"error": f"Unknown task type: {task_type}"}

    except Exception as e:
        print(f"❌ Handler Error: {e}")
        print(traceback.format_exc())
        return {
            "error": str(e), 
            "trace": traceback.format_exc()
        }

# Start RunPod serverless worker
start({"handler": handler})