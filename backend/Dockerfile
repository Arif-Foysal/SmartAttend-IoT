# Use Miniconda to get pre-built binaries (Conda-forge has dlib binaries!)
FROM continuumio/miniconda3

# Essential system dependencies (git for pip install git+...)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install dlib from conda-forge (Pre-compiled Binary - No compiling needed!)
# This is the magic step that prevents the build from getting stuck.
RUN conda install -y -c conda-forge dlib

WORKDIR /app

COPY requirements.txt .

# Install other dependencies via pip
# Pip will detect that 'dlib' is already installed by conda and skip compiling it.
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
