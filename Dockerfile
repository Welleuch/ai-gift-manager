FROM runpod/worker-comfyui:5.0.0-base

# 1. Copy the startup script
COPY start_worker.sh /start_worker.sh
RUN chmod +x /start_worker.sh

# 2. Copy model config
COPY extra_model_paths.yaml /comfyui/extra_model_paths.yaml

# 3. Set entrypoint to our script
CMD ["/start_worker.sh"]
