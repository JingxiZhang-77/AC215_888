# Frontend Configuration

# Flask settings
DEBUG = False
HOST = '0.0.0.0'
PORT = 8080

# File upload settings
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

# GCP settings
GCP_PROJECT = "apcomp215-group88"
BUCKET_NAME = "group88-bucket-1"
GCP_LOCATION = "us-central1"
GENERATIVE_MODEL = "gemini-2.5-flash"
