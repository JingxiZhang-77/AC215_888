"""
Shared pytest fixtures for Safety Event Classification API tests

Provides common test utilities, mock data, and authentication helpers.
Following cheese-app-ci-cd reference pattern.
"""

import pytest
import sys
from pathlib import Path

# Add src/api to path for imports - this is the key difference from the old structure
# Now tests/ is at root level, parallel to src/
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "api"))


@pytest.fixture
def sample_incident_descriptions():
    """Sample incident descriptions for testing classification"""
    return {
        "sse": "Patient received wrong medication and suffered severe allergic reaction requiring ICU admission.",
        "pse": "Nurse noticed wrong medication was prepared but caught it before administration to patient.",
        "nme": "Pharmacy system flagged drug interaction before order was processed. No medication reached patient.",
        "nse": "Patient complained about cold food. No safety concerns identified.",
    }


@pytest.fixture
def valid_departments():
    """List of valid department values"""
    return [
        "internal medicine",
        "surgery",
        "ob/gyn/nicu",
        "radiology/imaging",
        "outpatient/ER"
    ]


@pytest.fixture
def test_user_credentials():
    """Test user credentials for authentication"""
    return {
        "username": "admin",
        "password": "admin123"
    }


@pytest.fixture
def auth_headers(test_user_credentials):
    """
    Get authentication headers for protected endpoints.
    Used in integration and system tests.
    """
    from utils.auth import create_access_token
    
    token = create_access_token({
        "username": test_user_credentials["username"],
        "role": "admin",
        "email": "admin@hospital.com",
        "department": "internal medicine"
    })
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_chinese_text():
    """Sample Chinese text for translation testing"""
    return {
        "simplified": "患者在走廊摔倒，头部受伤",
        "traditional": "患者在走廊摔倒，頭部受傷",
    }


@pytest.fixture
def sample_spanish_text():
    """Sample Spanish text for translation testing"""
    return "El paciente se cayó en el pasillo y sufrió lesiones en la cabeza"


@pytest.fixture
def sample_french_text():
    """Sample French text for translation testing"""
    return "Le patient est tombé dans le couloir et s'est blessé à la tête"
