FROM runpod/worker-comfyui:5.0.0-base

# ------------------------------------------------------------------------------
# BAKING CUSTOM NODES
# We install these during the build so they are instant at runtime.
# ------------------------------------------------------------------------------

# 1. ComfyUI-HunyuanWorldnode
# Required for: 'Hunyuan3Dv2Conditioning', 'VAEDecodeHunyuan3D', 'SaveGLB', 'VoxelToMesh'
RUN comfy-node-install https://github.com/A043-studios/ComfyUI_HunyuanWorldnode

# 2. ComfyUI-RMBG
# Required for: 'BiRefNetRMBG'
RUN comfy-node-install https://github.com/1038lab/ComfyUI-RMBG

# 3. ComfyUI-KJNodes
# Good to have for general utility and missing nodes often found in workflows
RUN comfy-node-install https://github.com/kijai/ComfyUI-KJNodes

# ------------------------------------------------------------------------------
# MODEL STRATEGY
# ------------------------------------------------------------------------------
# Copy the extra paths config so ComfyUI knows where to find models on the volume
COPY extra_model_paths.yaml /comfyui/extra_model_paths.yaml

# The base image automatically starts ComfyUI. 
# We don't need to explicitly pass --extra-model-paths-config if we place it where ComfyUI looks,
# OR we can rely on standard loading. 
# However, runpod-workers/worker-comfyui usually allows arguments via environment variables or expected paths.
# A safe bet is to putting it in the root or `models` folder if the base supports it.
# Better yet, the handler might ignore it. 
# Let's just ensure it's there. The best way with this image is often to bake or mount.
# But since we are mounting, we need this file.

