# Multi-stage Railway Dockerfile for REJLERS Backend
# Advanced deployment strategy with proper Python environment

FROM python:3.11-slim AS base

# Set environment variables for Railway compatibility
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=config.settings.railway

# Set work directory
WORKDIR /app

# Install system dependencies for Railway
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r rejlers && useradd -r -g rejlers rejlers

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies with explicit pip path
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p /app/static /app/staticfiles /app/media && \
    chown -R rejlers:rejlers /app

# Switch to non-root user
USER rejlers

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Use advanced startup manager
CMD ["python", "manage_railway.py", "web"]