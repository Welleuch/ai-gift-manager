FROM runpod/worker-comfyui:5.0.0-base

# 1. Copy the startup script
COPY start_worker.sh /start_worker.sh
RUN chmod +x /start_worker.sh

# 2. Copy model config
COPY extra_model_paths.yaml /comfyui/extra_model_paths.yaml

# 3. Fix Windows line endings (CRLF) and set permission
RUN sed -i 's/\r$//' /start_worker.sh && chmod +x /start_worker.sh

# 4. Set entrypoint
CMD ["/bin/bash", "/start_worker.sh"]
