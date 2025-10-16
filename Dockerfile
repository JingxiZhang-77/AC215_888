# Use the official Debian-hosted Python image
FROM python:3.11-slim-bookworm

# Environment setup
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1

# uv settings (dependency manager)
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/home/app/.venv

# Google credentials default path 
ENV GOOGLE_APPLICATION_CREDENTIALS=/secrets/llm-service-account.json

# Install system dependencies and uv
RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install uv && \
    useradd -ms /bin/bash app -d /home/app -u 1000 && \
    mkdir -p /app /secrets && \
    chown -R app:app /app /secrets

# Switch to non-root user
USER app
WORKDIR /app

# Copy all files into container
COPY --chown=app:app . /app

# Install Python dependencies from pyproject.toml
RUN uv sync

# Run main script directly on startup
ENTRYPOINT ["uv", "run", "python", "src/model/execution2.py"]

