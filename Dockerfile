# Use Ubuntu 24.04 base
FROM ubuntu:24.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies + PrusaSlicer dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    git \
    wget \
    xvfb \
    python3 \
    python3-pip \
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
    libgtk-3-0 \
    libglew2.2 \
    && rm -rf /var/lib/apt/lists/*

# Install PrusaSlicer from official GitHub release
RUN PRUSA_VERSION=2.7.1 && \
    wget -O /tmp/prusa.tar.bz2 "https://github.com/prusa3d/PrusaSlicer/releases/download/version_${PRUSA_VERSION}/PrusaSlicer-${PRUSA_VERSION}+linux-x64-GTK3-202312121425.tar.bz2" && \
    mkdir -p /opt/prusa-slicer && \
    tar -xjf /tmp/prusa.tar.bz2 -C /opt/prusa-slicer --strip-components=1 && \
    ln -s /opt/prusa-slicer/prusa-slicer /usr/local/bin/prusa-slicer && \
    rm /tmp/prusa.tar.bz2

# Set display environment variable for headless GUI apps
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Copy ALL project files
COPY . .

# Install Python dependencies
RUN pip3 install -r requirements.txt --break-system-packages

# Ensure handler is executable
RUN chmod +x /app/handler.py

# Verify installations
RUN python3 --version && \
    prusa-slicer --help > /dev/null && \
    echo "✓ All dependencies installed successfully"

# Start the RunPod serverless handler
CMD ["python3", "-u", "/app/handler.py"]