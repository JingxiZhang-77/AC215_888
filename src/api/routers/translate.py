from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from google.cloud import translate_v2 as translate
from google.api_core import exceptions as google_exceptions
from utils.lang import detect_language
from utils.logger import logger
import os

router = APIRouter()

# Initialize Google Translate client
try:
    # Set quota project via environment variable
    gcp_project = os.getenv("GCP_PROJECT", "apcomp215-group88")
    os.environ["GOOGLE_CLOUD_QUOTA_PROJECT"] = gcp_project
    translate_client = translate.Client()
    TRANSLATION_AVAILABLE = True
    logger.info(f"Google Translate client initialized with quota project: {gcp_project}")
except Exception as e:
    logger.warning(f"Google Translate client initialization failed: {e}")
    translate_client = None
    TRANSLATION_AVAILABLE = False


class TranslateRequest(BaseModel):
    text: str = Field(min_length=1, description="Text to translate")


class TranslateResponse(BaseModel):
    original_text: str
    detected_lang: str
    translated_text: str
    was_translated: bool
    engine: str
    error: str = None


def fallback_translate(text: str, lang: str) -> str:
    """
    Fallback translation when Google Translate is not available
    Provides a clear indication that the text needs translation

    Supported languages:
    - zh-CN: Simplified Chinese
    - zh-TW: Traditional Chinese
    - es: Spanish
    - fr: French
    """
    lang_names = {
        "zh-CN": "Simplified Chinese",
        "zh-TW": "Traditional Chinese",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "es": "Spanish",
        "fr": "French",
    }
    lang_name = lang_names.get(lang, lang)

    # Return a more informative message
    return f"[Translation not available - Original {lang_name} text] {text}"


@router.post("/translate", response_model=TranslateResponse)
def translate_text(req: TranslateRequest):
    """
    Translate text to English using Google Translate API

    Automatically detects the source language and translates to English.
    Falls back to indicating translation unavailability if API is disabled.
    """
    try:
        # Detect language
        lang = detect_language(req.text)

        # If already English, no translation needed
        if lang == "en":
            return TranslateResponse(
                original_text=req.text,
                detected_lang="en",
                translated_text=req.text,
                was_translated=False,
                engine="none",
            )

        # Check if Google Translate is available
        if not TRANSLATION_AVAILABLE or translate_client is None:
            logger.warning("Google Translate API not available")
            return TranslateResponse(
                original_text=req.text,
                detected_lang=lang,
                translated_text=fallback_translate(req.text, lang),
                was_translated=False,
                engine="fallback",
                error="Google Cloud Translation API is not enabled. Please enable it in your GCP project.",
            )

        # Use Google Translate API to translate to English
        logger.info(f"Translating from {lang} to English")

        try:
            # Google Translate uses 'zh-CN' and 'zh-TW' for Chinese variants
            # But also accepts 'zh' as simplified Chinese
            source_lang = lang
            if lang == "zh-CN":
                source_lang = "zh-CN"  # Simplified Chinese
            elif lang == "zh-TW":
                source_lang = "zh-TW"  # Traditional Chinese

            result = translate_client.translate(req.text, source_language=source_lang, target_language="en")

            translated_text = result["translatedText"]
            detected_lang = result.get("detectedSourceLanguage", lang)

            logger.info("Translation complete")

            return TranslateResponse(
                original_text=req.text,
                detected_lang=detected_lang,
                translated_text=translated_text,
                was_translated=True,
                engine="google_translate",
            )

        except google_exceptions.Forbidden as e:
            # API not enabled
            logger.error(f"Translation API forbidden: {e}")
            return TranslateResponse(
                original_text=req.text,
                detected_lang=lang,
                translated_text=fallback_translate(req.text, lang),
                was_translated=False,
                engine="fallback",
                error="Google Cloud Translation API is not enabled. Please enable it in your GCP project console.",
            )

    except Exception as e:
        logger.error(f"Translation error: {e}")
        # Fallback to indicating translation issue
        return TranslateResponse(
            original_text=req.text,
            detected_lang=detect_language(req.text) if req.text else "unknown",
            translated_text=req.text,
            was_translated=False,
            engine="error",
            error=str(e),
        )
