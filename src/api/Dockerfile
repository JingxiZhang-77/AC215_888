FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# uv installs to /root/.local/bin by default
ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy project metadata and entrypoint early (for layer caching)
COPY pyproject.toml ./
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Copy full application source
COPY . .

# Create virtual environment and install dependencies
RUN uv venv
ENV PATH="/app/.venv/bin:${PATH}"

# Expose API port
EXPOSE 9000

# Use entrypoint script
ENTRYPOINT ["/bin/bash", "docker-entrypoint.sh"]
