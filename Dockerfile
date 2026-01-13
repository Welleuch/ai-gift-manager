# Use Ubuntu 24.04 base
FROM ubuntu:24.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# 1. Install system tools and enable the 'universe' repository
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository universe \
    && apt-get update

# 2. Install Python, Pip, and all PrusaSlicer dependencies
# We use the specific library names for Ubuntu 24.04 (Noble)
RUN apt-get install -y \
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

# 3. Install Python libraries
RUN pip3 install runpod boto3 requests python-dotenv --break-system-packages

# 4. Set working directory
WORKDIR /

# 5. Copy your local files into the Docker container
COPY . .

# 6. Ensure the handler is executable
RUN chmod +x /app/handler.py

# 7. Start the RunPod handler
CMD [ "python3", "-u", "/app/handler.py" ]