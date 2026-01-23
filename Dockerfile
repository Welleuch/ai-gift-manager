FROM runpod/worker-comfyui:5.0.0-base

# 1. TEMPORARILY DISABLED: Massive Custom Nodes
# We are creating a "Debug Build" to test if the base image + network allows the worker to start.
# If this works, we know the previous crash was due to 8GB image size or a broken node.

# 2. Configs
COPY extra_model_paths.yaml /comfyui/extra_model_paths.yaml

# 3. Install critical Python dependencies for handler.py
# If these are missing, handler.py crashes on import -> Infinite Initializing Loop
RUN pip install boto3 requests runpod

# 4. Create necessary volume link
RUN mkdir -p /runpod-volume

# 4. Standard Base Image CMD is used automatically.
# No changes to CMD or Entrypoint.
