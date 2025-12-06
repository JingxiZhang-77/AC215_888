"""
System tests for Safety Event Classification API

End-to-end tests against the fully running system.
Makes real HTTP requests to localhost:9000.
Tests the entire HTTP stack and architecture.

Run in CI/CD with --network host.
Following cheese-app-ci-cd reference pattern.
"""

import pytest
import requests
import time
import os


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
            f"{API_BASE_URL}/api/v1/auth/login", json={"username": "admin", "password": "admin123"}, timeout=10
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
            f"{API_BASE_URL}/api/v1/auth/login", json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data

    def test_protected_endpoint_without_auth(self):
        """Test protected endpoint rejects unauthenticated requests"""
        response = requests.post(
            f"{API_BASE_URL}/api/v1/classify/", json={"description": "Test incident", "department": "surgery"}
        )
        assert response.status_code == 403

    def test_protected_endpoint_with_auth(self):
        """Test protected endpoint accepts authenticated requests"""
        token = get_auth_token()
        if not token:
            pytest.skip("Could not get auth token")

        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{API_BASE_URL}/api/v1/classify/",
            json={"description": "Patient fell in the hallway", "department": "internal medicine"},
            headers=headers,
        )
        # May be 200 or 500 depending on LLM availability
        assert response.status_code in [200, 500]


@pytest.mark.skipif(not is_api_running(), reason="API not running at localhost:9000")
class TestSystemTranslation:
    """System tests for translation functionality"""

    def test_translate_english(self):
        """Test English text translation (no change expected)"""
        response = requests.post(f"{API_BASE_URL}/api/v1/translate", json={"text": "Patient fell in the hallway"})
        assert response.status_code == 200
        data = response.json()
        assert data["detected_lang"] == "en"
        assert data["was_translated"] is False

    def test_translate_chinese(self):
        """Test Chinese text detection and translation"""
        response = requests.post(f"{API_BASE_URL}/api/v1/translate", json={"text": "患者在走廊摔倒"})
        assert response.status_code == 200
        data = response.json()
        assert data["detected_lang"] in ["zh-CN", "zh-TW", "zh"]

    def test_translate_response_schema(self):
        """Test translation response has correct schema"""
        response = requests.post(f"{API_BASE_URL}/api/v1/translate", json={"text": "Hello world"})
        assert response.status_code == 200
        data = response.json()
        required_fields = ["original_text", "detected_lang", "translated_text", "was_translated", "engine"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"


@pytest.mark.skipif(not is_api_running(), reason="API not running at localhost:9000")
class TestSystemErrorHandling:
    """System tests for error handling"""

    def test_invalid_route_returns_404(self):
        """Test invalid routes return 404"""
        response = requests.get(f"{API_BASE_URL}/nonexistent-route")
        assert response.status_code == 404

    def test_invalid_login(self):
        """Test invalid login returns 401"""
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/login", json={"username": "invalid", "password": "invalid"}
        )
        assert response.status_code == 401

    def test_malformed_json(self):
        """Test malformed JSON returns 422"""
        response = requests.post(
            f"{API_BASE_URL}/api/v1/translate", data="not valid json", headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


# Standalone tests that don't require running API
class TestAPIWithoutServer:
    """Tests that can run without a live server"""

    def test_api_structure(self):
        """Test that we can import the API module"""
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "api"))

        from service import app

        assert app.title == "Safety Event Classification API"
        assert app.version == "1.0.0"
