# Use Debian Bullseye to get pre-compiled python3-dlib
FROM debian:bullseye-slim

# Install system dependencies
# python3-dlib avoids compiling dlib from source (which kills small servers)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dlib \
    libopenblas-dev \
    liblapack-dev \
    git \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Install dependencies
# We use system packages, so we don't need a venv
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Expose port and run
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
