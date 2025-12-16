FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    && rm -rf /var/lib/apt/lists/*

# Optimize for low-RAM build (Render free tier)
ENV CMAKE_ARGS="-DDLIB_USE_CUDA=0"
ENV MAX_JOBS=1

WORKDIR /app

COPY requirements.txt .

# Install dependencies (will compile dlib slowly but safely)
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
