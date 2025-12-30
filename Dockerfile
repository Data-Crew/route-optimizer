# Route Optimizer - Docker Image
# ================================
# Optimized for geospatial dependencies (GDAL, GEOS, PROJ)

FROM python:3.11-slim-bookworm

LABEL maintainer="Data Crew Consulting"
LABEL description="Modular route optimization system supporting CPP, TSP, and more"

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies for geospatial libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    # GDAL and geospatial
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    # Spatial indexing
    libspatialindex-dev \
    # Build tools (needed for some pip packages)
    gcc \
    g++ \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_CONFIG=/usr/bin/gdal-config

# Create app directory
WORKDIR /app

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory for results
RUN mkdir -p /app/output

# Default command: show available examples
CMD ["bash", "-c", "echo '🚗 Route Optimizer - Available Examples:' && echo '' && echo '  CPP (cover all streets):' && echo '    python parking_enforcement.py' && echo '' && echo '  TSP (visit points):' && echo '    python delivery_route.py' && echo '' && echo 'Run with: docker compose run --rm app python <example>.py'"]

