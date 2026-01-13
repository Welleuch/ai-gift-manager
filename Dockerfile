# Use Ubuntu 24.04 base
FROM ubuntu:24.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# 1. Manually enable 'universe' repository and install dependencies
# We edit the new Ubuntu 24.04 sources format directly
RUN apt-get update && apt-get install -y curl ca-certificates \
    && sed -i 's/Components: main restricted/Components: main restricted universe/' /etc/apt/sources.list.d/ubuntu.sources \
    && apt-get update && apt-get install -y \
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
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python libraries
# We use --break-system-packages because Ubuntu 24.04 enforces managed environments
RUN pip3 install runpod boto3 requests python-dotenv --break-system-packages

# 3. Set working directory
WORKDIR /

# 4. Copy your local files into the Docker container
COPY . .

# 5. Ensure the handler is executable
RUN chmod +x /app/handler.py

# 6. Start the RunPod handler
CMD [ "python3", "-u", "/app/handler.py" ]