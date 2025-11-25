"""
Unit tests for utility functions

Tests utility modules in isolation:
- Language detection (lang.py)
- Password hashing and verification (auth.py)
- Configuration settings (config.py)

No external dependencies required - fast execution.
"""

import pytest
import sys
import os

# Add API source to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))

from utils.lang import detect_language, pseudo_translate


class TestDetectLanguage:
    """Tests for language detection function"""

    def test_detect_english(self):
        """Test English text detection"""
        assert detect_language("Patient fell in the hallway") == "en"
        assert detect_language("The medication was administered correctly") == "en"
        assert detect_language("Hello world") == "en"

    def test_detect_simplified_chinese(self):
        """Test Simplified Chinese detection"""
        assert detect_language("患者在走廊摔倒") == "zh-CN"
        assert detect_language("医生给病人开了药") == "zh-CN"
        assert detect_language("这是简体中文") == "zh-CN"

    def test_detect_traditional_chinese(self):
        """Test Traditional Chinese detection"""
        # Traditional Chinese with specific characters
        assert detect_language("這是繁體中文") == "zh-TW"
        assert detect_language("醫院的體制") == "zh-TW"

    def test_detect_spanish(self):
        """Test Spanish text detection"""
        assert detect_language("El paciente se cayó") == "es"
        assert detect_language("¿Cómo está usted?") == "es"
        assert detect_language("La medicación fue administrada") == "es"

    def test_detect_french(self):
        """Test French text detection (requires French-specific characters not in Spanish)"""
        # French with ç, ê, î, ô, û, œ - characters unique to French (no é which also appears in Spanish)
        assert detect_language("Ça va bien") == "fr"  # ç is French-only
        assert detect_language("Le dîner") == "fr"  # î is French-only
        assert detect_language("Cœur") == "fr"  # œ is French-only

    def test_detect_japanese(self):
        """Test Japanese text detection (with hiragana/katakana)"""
        # Japanese with clear hiragana markers
        assert detect_language("こんにちは") == "ja"
        assert detect_language("ありがとう") == "ja"

    def test_detect_korean(self):
        """Test Korean text detection"""
        assert detect_language("환자가 복도에서 넘어졌습니다") == "ko"
        assert detect_language("안녕하세요") == "ko"

    def test_detect_empty_string(self):
        """Test empty string returns English as default"""
        assert detect_language("") == "en"
        assert detect_language("   ") == "en"

    def test_detect_mixed_content(self):
        """Test mixed content detection (Chinese takes precedence)"""
        # Chinese characters should be detected as Chinese
        assert detect_language("Hello 你好") in ["zh-CN", "zh-TW"]


class TestPseudoTranslate:
    """Tests for pseudo translation function"""

    def test_pseudo_translate_chinese(self):
        """Test pseudo translation for Chinese"""
        result = pseudo_translate("你好", "zh-CN")
        assert "[EN][auto from Simplified Chinese]" in result
        assert "你好" in result

    def test_pseudo_translate_spanish(self):
        """Test pseudo translation for Spanish"""
        result = pseudo_translate("Hola", "es")
        assert "[EN][auto from Spanish]" in result
        assert "Hola" in result

    def test_pseudo_translate_french(self):
        """Test pseudo translation for French"""
        result = pseudo_translate("Bonjour", "fr")
        assert "[EN][auto from French]" in result
        assert "Bonjour" in result

    def test_pseudo_translate_unknown_lang(self):
        """Test pseudo translation for unknown language code"""
        result = pseudo_translate("Test", "xx")
        assert "[EN][auto from xx]" in result
        assert "Test" in result
