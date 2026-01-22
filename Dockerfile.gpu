FROM runpod/worker-comfyui:5.0.0-base

# Consolidate all node installations into one layer to prevent RunPod build metadata timeouts
RUN cd /comfyui/custom_nodes && \
    git clone https://github.com/A043-studios/ComfyUI_HunyuanWorldnode && \
    git clone https://github.com/1038lab/ComfyUI-RMBG && \
    git clone https://github.com/kijai/ComfyUI-KJNodes && \
    cd ComfyUI-KJNodes && \
    pip install --no-cache-dir -r requirements.txt

# Strategy for models - ensures comfyui finds them on the network volume
COPY extra_model_paths.yaml /comfyui/extra_model_paths.yaml
