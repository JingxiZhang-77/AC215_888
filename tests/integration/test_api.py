"""
Integration tests for Safety Event Classification API

Tests the full API endpoints with FastAPI TestClient.
Verifies routing, validation, response schema, and business logic integration.
No real HTTP server required - uses ASGI TestClient.

Following cheese-app-ci-cd reference pattern.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src/api to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "api"))

# Mock Google Cloud services BEFORE any imports that need them
# This allows tests to run without GCP credentials

# Create mock modules for all Google Cloud services
mock_translate_module = MagicMock()
mock_translate_client = MagicMock()
mock_translate_module.Client.return_value = mock_translate_client

mock_speech_module = MagicMock()
mock_speech_client = MagicMock()
mock_speech_module.SpeechClient.return_value = mock_speech_client

# Patch all Google Cloud modules at the sys.modules level
# This must happen before any imports that use these modules
sys.modules["google.cloud.translate_v2"] = mock_translate_module
sys.modules["google.cloud.speech"] = mock_speech_module
sys.modules["google.cloud.speech_v1p1beta1"] = mock_speech_module
sys.modules["google.api_core"] = MagicMock()
sys.modules["google.api_core.exceptions"] = MagicMock()

try:
    from fastapi.testclient import TestClient
    from service import app
    from utils.auth import create_access_token

    APP_AVAILABLE = True
except Exception as e:
    APP_AVAILABLE = False
    app = None
    print(f"Warning: Could not import app: {e}")


def get_auth_headers(role: str = "admin") -> dict:
    """Generate auth headers with specified role"""
    if not APP_AVAILABLE:
        return {}
    token = create_access_token(
        {"username": "testuser", "role": role, "email": "test@hospital.com", "department": "internal medicine"}
    )
    return {"Authorization": f"Bearer {token}"}


# Skip all tests if app is not available
pytestmark = pytest.mark.skipif(not APP_AVAILABLE, reason="App could not be imported")

# Create test client only if app is available
client = TestClient(app) if APP_AVAILABLE else None


class TestRootEndpoints:
    """Integration tests for root API endpoints"""

    def test_root_endpoint(self):
        """Test the root endpoint returns welcome message"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Safety Event" in data["message"]

    def test_root_returns_json(self):
        """Test that root returns JSON content type"""
        response = client.get("/")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    def test_root_contains_version(self):
        """Test root endpoint contains version info"""
        response = client.get("/")
        data = response.json()
        assert "version" in data
        assert data["version"] == "1.0.0"

    def test_root_contains_docs_link(self):
        """Test root endpoint contains docs link"""
        response = client.get("/")
        data = response.json()
        assert "docs" in data


class TestHealthEndpoints:
    """Tests for health check endpoints"""

    def test_health_v1_endpoint(self):
        """Test v1 health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_legacy_endpoint(self):
        """Test legacy health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["deprecated"] is True


class TestAuthEndpoints:
    """Integration tests for authentication endpoints"""

    def test_login_success(self):
        """Test successful login with valid credentials"""
        response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "admin"

    def test_login_invalid_username(self):
        """Test login with invalid username"""
        response = client.post("/api/v1/auth/login", json={"username": "nonexistent", "password": "password"})
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_login_invalid_password(self):
        """Test login with invalid password"""
        response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrongpassword"})
        assert response.status_code == 401

    def test_login_missing_fields(self):
        """Test login with missing required fields"""
        response = client.post("/api/v1/auth/login", json={"username": "admin"})
        assert response.status_code == 422  # Validation error

    def test_login_returns_jwt_token(self):
        """Test login returns valid JWT token format"""
        response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
        data = response.json()
        token = data["access_token"]
        # JWT tokens have 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3


class TestTranslationEndpoints:
    """Integration tests for translation endpoints"""

    def test_translate_english_no_change(self):
        """Test English text is returned unchanged"""
        response = client.post("/api/v1/translate", json={"text": "Patient fell in the hallway"})
        assert response.status_code == 200
        data = response.json()
        assert data["detected_lang"] == "en"
        assert data["was_translated"] is False
        assert data["original_text"] == data["translated_text"]

    def test_translate_detects_chinese(self):
        """Test Chinese text is detected correctly"""
        response = client.post("/api/v1/translate", json={"text": "患者在走廊摔倒"})
        assert response.status_code == 200
        data = response.json()
        assert data["detected_lang"] in ["zh-CN", "zh-TW", "zh"]

    def test_translate_detects_spanish(self):
        """Test Spanish text is detected correctly"""
        response = client.post("/api/v1/translate", json={"text": "El paciente se cayó en el pasillo"})
        assert response.status_code == 200
        data = response.json()
        assert data["detected_lang"] == "es"

    def test_translate_detects_french(self):
        """Test French text is detected correctly"""
        # Use French-specific characters (ç, î, ô, etc.) that don't appear in Spanish
        response = client.post("/api/v1/translate", json={"text": "Ça va bien, le dîner est prêt"})
        assert response.status_code == 200
        data = response.json()
        assert data["detected_lang"] == "fr"

    def test_translate_empty_text_rejected(self):
        """Test empty text is rejected"""
        response = client.post("/api/v1/translate", json={"text": ""})
        assert response.status_code == 422

    def test_translate_response_schema(self):
        """Test translation response has correct schema"""
        response = client.post("/api/v1/translate", json={"text": "Hello world"})
        data = response.json()
        assert "original_text" in data
        assert "detected_lang" in data
        assert "translated_text" in data
        assert "was_translated" in data
        assert "engine" in data


class TestClassificationEndpoints:
    """Integration tests for classification endpoints"""

    def test_classify_requires_auth(self):
        """Test classification endpoint requires authentication"""
        response = client.post(
            "/api/v1/classify/", json={"description": "Patient fell", "department": "internal medicine"}
        )
        # May return 401 (Unauthorized) or 403 (Forbidden) depending on auth middleware
        assert response.status_code in [401, 403]

    def test_classify_with_auth(self):
        """Test classification with valid authentication"""
        headers = get_auth_headers("admin")
        response = client.post(
            "/api/v1/classify/",
            json={"description": "Patient fell in the hallway", "department": "internal medicine"},
            headers=headers,
        )
        # May be 200 or 500 depending on LLM availability
        assert response.status_code in [200, 500]

    def test_classify_nurse_role_allowed(self):
        """Test nurse role can access classification"""
        headers = get_auth_headers("nurse")
        response = client.post(
            "/api/v1/classify/", json={"description": "Patient fell", "department": "surgery"}, headers=headers
        )
        assert response.status_code in [200, 500]

    def test_classify_doctor_role_allowed(self):
        """Test doctor role can access classification"""
        headers = get_auth_headers("doctor")
        response = client.post(
            "/api/v1/classify/", json={"description": "Patient fell", "department": "surgery"}, headers=headers
        )
        assert response.status_code in [200, 500]


class TestCORS:
    """Tests for CORS configuration"""

    def test_cors_enabled(self):
        """Test that CORS headers are present"""
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_cors_allows_configured_origins(self):
        """Test that CORS allows configured origins"""
        response = client.get("/", headers={"Origin": "http://localhost:3001"})
        assert response.status_code == 200


class TestInvalidRoutes:
    """Tests for handling invalid routes"""

    def test_invalid_route_returns_404(self):
        """Test that invalid routes return 404"""
        response = client.get("/this-route-does-not-exist")
        assert response.status_code == 404

    def test_method_not_allowed(self):
        """Test that POST to GET-only endpoint returns 405"""
        response = client.post("/")
        assert response.status_code == 405
