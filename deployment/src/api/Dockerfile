FROM python:3.11-slim-bookworm

ARG DEBIAN_PACKAGES="build-essential ffmpeg libsndfile1 curl"

# Non-interactive apt & locale
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1

# uv configuration (copy wheels, project venv path)
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/home/app/.venv
ENV GOOGLE_APPLICATION_CREDENTIALS=/secrets/llm-service-account.json

# System setup + uv install + non-root user
RUN set -ex; \
    for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends $DEBIAN_PACKAGES && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install uv && \
    useradd -ms /bin/bash app -d /home/app -u 1000 && \
    mkdir -p /app && chown app:app /app && \
    mkdir -p /secrets && chown app:app /secrets && \
    mkdir -p /home/app/.venv && chown app:app /home/app/.venv

USER app
WORKDIR /app

# Copy dependency files first for better layer caching
COPY --chown=app:app pyproject.toml ./

# Create virtual environment and install dependencies (includes test deps)
RUN uv venv && uv sync

# Add venv to PATH so commands are available
ENV PATH="/home/app/.venv/bin:${PATH}"

# Copy API source code
COPY --chown=app:app . .

# Copy tests and pytest.ini from root (when building from root context)
# These will be copied via CI workflow or build script
# Tests are expected at /app/tests/ after docker cp or volume mount

# Make entrypoint executable
RUN chmod +x docker-entrypoint.sh

EXPOSE 9000

ENTRYPOINT ["/bin/bash", "docker-entrypoint.sh"]
