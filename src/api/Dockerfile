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
ENV PATH="/root/.local/bin:${PATH}"

# Copy the entire repository so both api and model modules are available
WORKDIR /app
COPY . .

# Switch to API directory
WORKDIR /app/src/api

# Prepare entrypoint
RUN chmod +x docker-entrypoint.sh

# Create virtual environment and install dependencies
RUN uv venv
ENV PATH="/app/src/api/.venv/bin:${PATH}"
RUN pip install --upgrade pip && pip install -r pyproject.toml

# Expose API port
EXPOSE 9000

# Use entrypoint script
ENTRYPOINT ["/bin/bash", "docker-entrypoint.sh"]
