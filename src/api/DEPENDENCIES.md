# API Dependencies Installation Guide

This guide provides the exact `uv add` commands to install all required dependencies for the Safety Event Classification API.

## 🔧 Installation Instructions

Run these commands **inside the Docker container** after starting it with `./docker-shell.sh`:

### 1. Core Web Framework
```bash
uv add "fastapi>=0.109.0"
uv add "uvicorn[standard]>=0.27.0"
```

### 2. Data Validation & Settings
```bash
uv add "pydantic>=2.5.0"
uv add "pydantic-settings>=2.1.0"
```

### 3. Authentication & Security
```bash
uv add "python-jose[cryptography]>=3.3.0"
uv add "passlib[bcrypt]>=1.7.4"
```

### 4. File Handling
```bash
uv add "python-multipart>=0.0.6"
```

### 5. Google Cloud AI Services
```bash
uv add "google-genai>=1.0.0"
uv add "google-cloud-speech>=2.24.0"
uv add "google-cloud-translate>=3.14.0"
```

### 6. Data Processing
```bash
uv add "pandas>=2.1.4"
uv add "openpyxl>=3.1.2"
```

### 7. Audio Processing
```bash
uv add "pydub>=0.25.1"
```

---

## 📋 All-in-One Installation (Copy-Paste)

If you prefer to install everything at once:

```bash
uv add \
  "fastapi>=0.109.0" \
  "uvicorn[standard]>=0.27.0" \
  "pydantic>=2.5.0" \
  "pydantic-settings>=2.1.0" \
  "python-jose[cryptography]>=3.3.0" \
  "passlib[bcrypt]>=1.7.4" \
  "python-multipart>=0.0.6" \
  "google-genai>=1.0.0" \
  "google-cloud-speech>=2.24.0" \
  "google-cloud-translate>=3.14.0" \
  "pandas>=2.1.4" \
  "openpyxl>=3.1.2" \
  "pydub>=0.25.1"
```

---

## 🚀 Complete Setup Workflow

```bash
# 1. Start Docker container
cd src/api
./docker-shell.sh

# 2. Inside container - Install dependencies
uv add \
  "fastapi>=0.109.0" \
  "uvicorn[standard]>=0.27.0" \
  "pydantic>=2.5.0" \
  "pydantic-settings>=2.1.0" \
  "python-jose[cryptography]>=3.3.0" \
  "passlib[bcrypt]>=1.7.4" \
  "python-multipart>=0.0.6" \
  "google-genai>=1.0.0" \
  "google-cloud-speech>=2.24.0" \
  "google-cloud-translate>=3.14.0" \
  "pandas>=2.1.4" \
  "openpyxl>=3.1.2" \
  "pydub>=0.25.1"

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Start API server
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

---

## ✅ Verification

After installation, verify everything is working:

```bash
# Check installed packages
uv pip list

# Test API health endpoint
curl http://localhost:9000/api/health

# Access interactive docs
# Open browser: http://localhost:9000/api/docs
```

---

## 📝 Notes

- **uv automatically resolves versions** - It will choose compatible versions for all dependencies
- **Lock file generated** - `uv.lock` will be created to ensure reproducible installs
- **Volume mounted** - Changes persist on your host machine at `src/api/`
- **No need to rebuild Docker** - Just install packages once inside the container

---

## 🔄 Future Installs

After the initial setup, when you restart the container:

1. Start container: `./docker-shell.sh`
2. Activate venv: `source .venv/bin/activate`
3. Start server: `uvicorn main:app --host 0.0.0.0 --port 9000 --reload`

Dependencies are already installed (persisted via volume mount), no need to reinstall.

---

## 🐛 Troubleshooting

### If dependencies are missing:
```bash
# Inside container
uv sync  # Installs from uv.lock
```

### If you want a fresh install:
```bash
# Inside container
rm -rf .venv uv.lock
uv venv
uv add [packages...]
```

### If uv command not found:
```bash
# Add to PATH
export PATH="/root/.local/bin:${PATH}"
```
