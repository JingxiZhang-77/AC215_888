"""
System tests for Safety Event Classification API

End-to-end tests against the fully running system.
Makes real HTTP requests to localhost:9000.
Tests the entire HTTP stack and architecture.

Run in CI/CD and locally using Docker with --network host.
"""

import pytest
import requests
import time
import sys
import os

# Add API source to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))


# Base URL for the API (assumes API is running)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:9000")


def is_api_running():
    """Check if API is accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def get_auth_token():
    """Get authentication token for protected endpoints"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception:
        pass
    return None


@pytest.mark.skipif(not is_api_running(), reason="API not running at localhost:9000")
class TestSystemRootEndpoints:
    """System tests for root API endpoints"""

    def test_root_endpoint(self):
        """Test the root endpoint returns welcome message"""
        response = requests.get(f"{API_BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Safety Event" in data["message"]

    def test_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{API_BASE_URL}/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_api_response_time(self):
        """Test API responds within acceptable time"""
        start = time.time()
        response = requests.get(f"{API_BASE_URL}/")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 2.0  # Should respond within 2 seconds


@pytest.mark.skipif(not is_api_running(), reason="API not running at localhost:9000")
class TestSystemAuthentication:
    """System tests for authentication flow"""

    def test_login_flow(self):
        """Test complete login flow"""
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data

    def test_protected_endpoint_without_auth(self):
        """Test protected endpoint rejects unauthenticated requests"""
        response = requests.post(
            f"{API_BASE_URL}/api/v1/classify/",
            json={"description": "Test incident", "department": "surgery"}
        )
        assert response.status_code == 403

    def test_protected_endpoint_with_auth(self):
        """Test protected endpoint accepts authenticated requests"""
        token = get_auth_token()
        assert token is not None, "Failed to get auth token"
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{API_BASE_URL}/api/v1/classify/",
            json={"description": "Patient fell in the hallway", "department": "internal medicine"},
            headers=headers,
            timeout=60  # Classification may take time
        )
        # Accept 200 (success) or 500 (LLM not available in CI)
        assert response.status_code in [200, 500]


@pytest.mark.skipif(not is_api_running(), reason="API not running at localhost:9000")
class TestSystemTranslation:
    """System tests for translation endpoints"""

    def test_translate_english(self):
        """Test English text translation (no change)"""
        response = requests.post(
            f"{API_BASE_URL}/api/v1/translate",
            json={"text": "Patient fell in the hallway"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["detected_lang"] == "en"
        assert data["was_translated"] is False

    def test_translate_chinese(self):
        """Test Chinese text detection and translation"""
        response = requests.post(
            f"{API_BASE_URL}/api/v1/translate",
            json={"text": "患者在走廊摔倒，需要紧急处理"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["detected_lang"] in ["zh-CN", "zh-TW", "zh"]

    def test_translate_spanish(self):
        """Test Spanish text detection"""
        response = requests.post(
            f"{API_BASE_URL}/api/v1/translate",
            json={"text": "El paciente se cayó en el pasillo"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["detected_lang"] == "es"

    def test_translate_french(self):
        """Test French text detection"""
        response = requests.post(
            f"{API_BASE_URL}/api/v1/translate",
            json={"text": "Le patient est tombé dans le couloir"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["detected_lang"] == "fr"


@pytest.mark.skipif(not is_api_running(), reason="API not running at localhost:9000")
class TestSystemClassification:
    """System tests for classification with full authentication"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication for classification tests"""
        self.token = get_auth_token()
        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def test_classify_incident(self):
        """Test incident classification with authentication"""
        if not self.token:
            pytest.skip("Could not obtain auth token")
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/classify/",
            json={
                "description": "Nurse noticed medication label was incorrect but corrected before administration",
                "department": "internal medicine"
            },
            headers=self.headers,
            timeout=60
        )
        # Accept 200 or 500 (LLM may not be available in CI)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "classification_code" in data or "final_classification_code" in data

    def test_classify_different_departments(self):
        """Test classification with different departments"""
        if not self.token:
            pytest.skip("Could not obtain auth token")
        
        departments = ["surgery", "ob/gyn/nicu", "radiology/imaging"]
        
        for dept in departments:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/classify/",
                json={
                    "description": "Equipment malfunction during procedure",
                    "department": dept
                },
                headers=self.headers,
                timeout=60
            )
            assert response.status_code in [200, 500], f"Failed for department: {dept}"


@pytest.mark.skipif(not is_api_running(), reason="API not running at localhost:9000")
class TestSystemDocumentation:
    """System tests for API documentation"""

    def test_openapi_schema(self):
        """Test OpenAPI schema is accessible"""
        response = requests.get(f"{API_BASE_URL}/api/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_swagger_docs(self):
        """Test Swagger documentation is accessible"""
        response = requests.get(f"{API_BASE_URL}/api/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_redoc_docs(self):
        """Test ReDoc documentation is accessible"""
        response = requests.get(f"{API_BASE_URL}/api/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


# Standalone tests that don't require running API
class TestAPIWithoutServer:
    """Tests that can run without a live server"""

    def test_api_module_importable(self):
        """Test that we can import the API module"""
        from service import app
        assert app.title == "Safety Event Classification API"
        assert app.version == "1.0.0"

    def test_routers_registered(self):
        """Test that all expected routers are registered"""
        from service import app
        
        routes = [route.path for route in app.routes]
        
        # Check key routes exist
        assert "/" in routes
        assert "/api/v1/health" in routes
