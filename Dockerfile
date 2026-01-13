# Use the latest Ubuntu 24.04 for the best library support
FROM ubuntu:24.04

# 1. Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# 2. Install Python, Pip, and ALL PrusaSlicer dependencies
# We include every library we discovered during our debugging sessions
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

# 3. Install the Python libraries for RunPod, Cloudflare R2, and APIs
# Note: --break-system-packages is a new requirement for Ubuntu 24.04+
RUN pip3 install \
    runpod \
    boto3 \
    requests \
    python-dotenv \
    --break-system-packages

# 4. Create the application directory
WORKDIR /app

# 5. Copy your code and config files into the image
# (We will create these in the next steps)
COPY . .

# 6. Make sure the Slicer path is standard
ENV PRUSA_PATH="/usr/bin/prusaslicer"

# 7. Start the RunPod Serverless handler
CMD [ "python3", "-u", "handler.py" ]