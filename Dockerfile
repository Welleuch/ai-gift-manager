# Use Ubuntu 24.04 for the latest GLIBC and library support
FROM ubuntu:24.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# 1. Install Python, Pip, and all PrusaSlicer system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    prusaslicer \
    libwebkit2gtk-4.1-0 \
    libasound2t64 \
    libatk1.0-0t64 \
    libglu1-mesa \
    libxcursor1 \
    libxinerama1 \
    libdbus-1-3 \
    libxrandr2 \
    libnss3 \
    libgbm1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python libraries
# We use --break-system-packages because Ubuntu 24.04 requires it for global pip installs
RUN pip3 install runpod boto3 requests python-dotenv --break-system-packages

# 3. Set the working directory to root
WORKDIR /

# 4. Copy everything from your GitHub repo to the root of the container
# This puts config.ini at /config.ini and your workflows at /workflows/
COPY . .

# 5. Start the RunPod handler
# Note: We assume handler.py is inside the 'app' folder based on your previous structure
CMD [ "python3", "-u", "/app/handler.py" ]