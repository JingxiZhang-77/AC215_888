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
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Create virtual environment and install dependencies
RUN uv venv
RUN uv pip install --no-cache-dir -r pyproject.toml

# Copy application code
COPY . .

# Expose API port
EXPOSE 9000

# Use entrypoint script
ENTRYPOINT ["/bin/bash", "docker-entrypoint.sh"]
