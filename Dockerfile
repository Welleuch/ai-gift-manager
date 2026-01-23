FROM runpod/worker-comfyui:5.0.0-base

# 1. PRE-INSTALL Nodes (Cache Strategy)
# We install these at build time to avoid runtime downloads
SHELL ["/bin/bash", "-c"]

WORKDIR /comfyui/custom_nodes

# Shallow clone to save space
RUN git clone --depth 1 https://github.com/A043-studios/ComfyUI_HunyuanWorldnode && \
    git clone --depth 1 https://github.com/1038lab/ComfyUI-RMBG && \
    git clone --depth 1 https://github.com/kijai/ComfyUI-KJNodes && \
    cd ComfyUI-KJNodes && \
    pip install --no-cache-dir --prefer-binary -r requirements.txt

# 2. Configs
COPY extra_model_paths.yaml /comfyui/extra_model_paths.yaml

# 3. Create necessary volume link
RUN mkdir -p /runpod-volume

# 4. Use the OFFICIAL handler, NOT our custom one for the GPU worker
# The base image already has a handler that works with standard ComfyUI API
# We DO NOT overwrite CMD. We let the base image handle the startup.
# The base image CMD is typically: CMD [ "python", "-u", "/rp_handler.py" ]
