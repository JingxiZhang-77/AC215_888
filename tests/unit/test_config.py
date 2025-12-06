"""
Unit tests for configuration settings

Tests configuration loading and default values.
No external dependencies required - fast execution.
Following cheese-app-ci-cd reference pattern.
"""

import pytest
from utils.config import Settings, settings


class TestSettings:
    """Tests for Settings configuration class"""

    def test_settings_instance_exists(self):
        """Test that global settings instance exists"""
        assert settings is not None
        assert isinstance(settings, Settings)

    def test_app_name_default(self):
        """Test default APP_NAME setting"""
        assert settings.APP_NAME == "Safety Event Classification API"

    def test_port_default(self):
        """Test default PORT setting"""
        assert settings.PORT == 9000

    def test_jwt_algorithm(self):
        """Test JWT algorithm setting"""
        assert settings.JWT_ALGORITHM == "HS256"

    def test_jwt_expiration_hours(self):
        """Test JWT expiration hours default"""
        assert settings.JWT_EXPIRATION_HOURS == 24
        assert isinstance(settings.JWT_EXPIRATION_HOURS, int)

    def test_valid_departments(self):
        """Test valid departments list"""
        expected_departments = ["internal medicine", "surgery", "ob/gyn/nicu", "radiology/imaging", "outpatient/ER"]
        assert settings.VALID_DEPARTMENTS == expected_departments

    def test_supported_audio_formats(self):
        """Test supported audio formats list"""
        assert "mp3" in settings.SUPPORTED_AUDIO_FORMATS
        assert "wav" in settings.SUPPORTED_AUDIO_FORMATS
        assert "m4a" in settings.SUPPORTED_AUDIO_FORMATS

    def test_supported_languages(self):
        """Test supported languages list"""
        assert "en-US" in settings.SUPPORTED_LANGUAGES
        assert "zh-CN" in settings.SUPPORTED_LANGUAGES

    def test_allowed_origins(self):
        """Test CORS allowed origins"""
        assert isinstance(settings.ALLOWED_ORIGINS, list)
        assert len(settings.ALLOWED_ORIGINS) > 0

    def test_gcp_region_default(self):
        """Test GCP region default"""
        assert settings.GCP_REGION == "us-central1"

    def test_llm_model_default(self):
        """Test LLM model default"""
        assert "gemini" in settings.LLM_MODEL.lower()

    def test_llm_temperature_range(self):
        """Test LLM temperature is in valid range"""
        assert 0 <= settings.LLM_TEMPERATURE <= 1

    def test_max_upload_size(self):
        """Test max upload size is reasonable"""
        assert settings.MAX_UPLOAD_SIZE_MB > 0
        assert settings.MAX_UPLOAD_SIZE_MB <= 100


class TestSettingsTypes:
    """Tests for correct Settings types"""

    def test_debug_is_bool(self):
        """Test DEBUG is boolean"""
        assert isinstance(settings.DEBUG, bool)

    def test_port_is_int(self):
        """Test PORT is integer"""
        assert isinstance(settings.PORT, int)

    def test_temperature_is_float(self):
        """Test LLM_TEMPERATURE is float"""
        assert isinstance(settings.LLM_TEMPERATURE, float)

    def test_lists_are_lists(self):
        """Test list settings are actually lists"""
        assert isinstance(settings.VALID_DEPARTMENTS, list)
        assert isinstance(settings.SUPPORTED_AUDIO_FORMATS, list)
        assert isinstance(settings.SUPPORTED_LANGUAGES, list)
