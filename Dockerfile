# Use the official Debian-hosted Python image
FROM python:3.11-slim-bookworm

# Set environment variables for uv (dependency manager)
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/home/app/.venv

# Ensure system dependencies are up-to-date, install Python tools,
# and create a non-root user for security
RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install uv && \
    useradd -ms /bin/bash app -d /home/app -u 1000 && \
    mkdir -p /src && \
    chown app:app /src

# Switch to non-root user and working directory
USER app
WORKDIR /app

# Copy source code and dependency definitions
COPY --chown=app:app . /app

# Install Python dependencies via uv (reads pyproject.toml)
RUN uv sync

# ==========================================================
# Entrypoint — automatically run your main script on startup
# ==========================================================

ENTRYPOINT ["uv", "run", "python", "src/model/execution2.py"]
