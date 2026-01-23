#!/bin/bash
set -ex

echo "--- 🚀 LIGHTWEIGHT WORKER STARTING ---"

# 0. Ensure volume directory exists to prevent config errors
mkdir -p /runpod-volume

# 1. Define custom node directory
NODE_DIR="/comfyui/custom_nodes"
mkdir -p $NODE_DIR
cd $NODE_DIR

# 2. Install HunyuanWorldnode if missing
if [ ! -d "ComfyUI_HunyuanWorldnode" ]; then
    echo "📦 Installing Hunyuan3D Node..."
    git clone --depth 1 https://github.com/A043-studios/ComfyUI_HunyuanWorldnode
else
    echo "✅ Hunyuan3D Node already exists."
fi

# 3. Install RMBG if missing
if [ ! -d "ComfyUI-RMBG" ]; then
    echo "📦 Installing RMBG Node..."
    git clone --depth 1 https://github.com/1038lab/ComfyUI-RMBG
else
    echo "✅ RMBG Node already exists."
fi

# 4. Install KJNodes if missing
if [ ! -d "ComfyUI-KJNodes" ]; then
    echo "📦 Installing KJNodes..."
    git clone --depth 1 https://github.com/kijai/ComfyUI-KJNodes
    
    echo "📦 Installing Requirements for KJNodes..."
    cd ComfyUI-KJNodes
    pip install --no-cache-dir --prefer-binary -r requirements.txt
    cd ..
else
    echo "✅ KJNodes already exists."
fi

# 5. Launch the standard RunPod Handler
echo "--- 🟢 STARTING COMFYUI HANDLER ---"
if [ -f "/rp_handler.py" ]; then
    exec python -u /rp_handler.py
elif [ -f "/handler.py" ]; then
    exec python -u /handler.py
else
    echo "❌ Could not find handler! Listing root..."
    ls -la /
    exit 1
fi
