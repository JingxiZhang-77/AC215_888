"""
Audio API Router

Endpoints for audio transcription without classification.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional, Dict
import tempfile
import os

from models.schemas import AudioTranscriptionResponse, LanguageEnum
from services.audio_service import audio_service
from utils.auth import require_role
from utils.logger import logger
from utils.config import settings

router = APIRouter()


@router.post(
    "/transcribe",
    response_model=AudioTranscriptionResponse,
    summary="Transcribe audio to text",
    description="Transcribe audio file with optional automatic translation to English"
)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file"),
    language: str = Form(default="en-US", description="Audio language code"),
    auto_translate: bool = Form(default=True, description="Auto-translate to English"),
    current_user: Dict = Depends(require_role("admin", "doctor", "nurse"))
):
    """
    Transcribe audio file to text
    
    Requires: admin, doctor, or nurse role
    
    Supported languages:
    - en-US: English
    - zh-CN: Mandarin (Simplified)
    - zh-HK: Cantonese
    - fr-FR: French
    - es-ES: Spanish
    
    Supported audio formats: mp3, wav, m4a, flac, ogg
    
    If auto_translate is true and audio is non-English, 
    the transcript will be automatically translated to English.
    """
    try:
        logger.info(f"Audio transcription request from user: {current_user['username']}")
        
        # Validate language
        if language not in settings.SUPPORTED_LANGUAGES:
            raise HTTPException(
                status_code=400,
                detail=f"Language '{language}' not supported. Supported: {', '.join(settings.SUPPORTED_LANGUAGES)}"
            )
        
        # Validate file type
        filename = file.filename.lower()
        if not any(filename.endswith(ext) for ext in ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm']):
            raise HTTPException(
                status_code=400,
                detail="Invalid audio format. Supported: mp3, wav, m4a, flac, ogg"
            )
        
        # Check file size
        if hasattr(file, 'size'):
            file_size_mb = file.size / (1024 * 1024)
            if file_size_mb > settings.AUDIO_MAX_FILE_SIZE_MB:
                raise HTTPException(
                    status_code=413,
                    detail=f"Audio file too large. Maximum: {settings.AUDIO_MAX_FILE_SIZE_MB}MB"
                )
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        try:
            # Transcribe and translate
            result = audio_service.transcribe_and_translate(
                tmp_path,
                language_code=language,
                auto_translate=auto_translate
            )
            
            logger.info(f"Transcription complete. Language: {result['original_language']}, Translated: {result['was_translated']}")
            
            return AudioTranscriptionResponse(
                transcript=result["transcript"],
                original_language=result["original_language"],
                was_translated=result["was_translated"],
                confidence=result["confidence"],
                duration_seconds=result.get("duration_seconds")
            )
            
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio transcription error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Audio transcription failed: {str(e)}"
        )


@router.get(
    "/languages",
    summary="List supported languages",
    description="Get list of supported languages for audio transcription"
)
async def list_supported_languages():
    """
    Get list of supported languages
    
    Returns language codes and names
    """
    from services.audio_service import SUPPORTED_LANGUAGES
    
    return {
        "languages": [
            {
                "code": code,
                "name": info["name"],
                "needs_translation": info["needs_translation"]
            }
            for code, info in SUPPORTED_LANGUAGES.items()
        ],
        "count": len(SUPPORTED_LANGUAGES)
    }
