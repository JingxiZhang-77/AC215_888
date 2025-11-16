"""
Classification API Router

REST endpoints for safety event classification.
Supports single incident, batch processing, and audio transcription with classification.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import tempfile
import os
import time

from models.schemas import (
    ClassificationRequest,
    ClassificationResult,
    BatchClassificationResponse,
    AudioClassificationRequest,
    AudioClassificationResponse,
    LanguageEnum
)
from services.classification_service import classification_service
from services.audio_service import audio_service
from utils.auth import require_role
from utils.logger import logger
from utils.config import settings

router = APIRouter()


@router.post(
    "/",
    response_model=ClassificationResult,
    summary="Classify single incident",
    description="Classify a single safety event incident with optional department specification"
)
async def classify_single(
    request: ClassificationRequest,
    current_user = Depends(require_role("admin", "doctor", "nurse"))
):
    """
    Classify a single safety incident
    
    Requires: admin, doctor, or nurse role
    
    Request body:
    ```json
    {
        "description": "Patient fell in hallway",
        "department": "internal medicine"
    }
    ```
    """
    try:
        logger.info(f"Classification request from user: {current_user['username']}")
        
        result = classification_service.classify_incident(
            description=request.description,
            department=request.department.value if request.department else None
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )


@router.post(
    "/batch",
    response_model=BatchClassificationResponse,
    summary="Classify multiple incidents from file",
    description="Upload CSV or Excel file with incident descriptions for batch classification"
)
async def classify_batch(
    file: UploadFile = File(..., description="CSV or Excel file with incidents"),
    current_user = Depends(require_role("admin", "doctor", "nurse"))
):
    """
    Classify multiple incidents from uploaded file
    
    Requires: admin, doctor, or nurse role
    
    File format:
    - CSV or Excel (.xlsx, .xls)
    - Must have a column with incident descriptions (e.g., 'Description', 'Incident', 'Event')
    - Optional 'Department' column for per-incident departments
    
    Example CSV:
    ```csv
    Description,Department
    Patient fell in hallway,internal medicine
    Wrong medication dose,surgery
    ```
    """
    try:
        logger.info(f"Batch classification request from user: {current_user['username']}")
        
        # Validate file type
        filename = file.filename.lower()
        if not any(filename.endswith(ext) for ext in ['.csv', '.xlsx', '.xls']):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Supported: CSV, Excel (.xlsx, .xls)"
            )
        
        # Check file size
        file_size_mb = 0
        if hasattr(file, 'size'):
            file_size_mb = file.size / (1024 * 1024)
            if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB"
                )
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        try:
            # Process file
            start_time = time.time()
            results, dept_stats = classification_service.process_file(tmp_path)
            processing_time = time.time() - start_time
            
            logger.info(f"Batch processing complete: {len(results)} incidents in {processing_time:.2f}s")
            
            return BatchClassificationResponse(
                results=results,
                count=len(results),
                processing_time=processing_time,
                department_statistics=dept_stats
            )
            
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch classification error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch classification failed: {str(e)}"
        )


@router.post(
    "/audio",
    response_model=AudioClassificationResponse,
    summary="Transcribe and classify audio incident",
    description="Upload audio file for transcription and classification. Supports multiple languages with auto-translation."
)
async def classify_audio(
    file: UploadFile = File(..., description="Audio file (mp3, wav, m4a, etc.)"),
    language: str = Form(default="en-US", description="Audio language code"),
    department: Optional[str] = Form(default=None, description="Department name"),
    auto_translate: bool = Form(default=True, description="Auto-translate to English"),
    current_user = Depends(require_role("admin", "doctor", "nurse"))
):
    """
    Transcribe audio and classify the incident
    
    Requires: admin, doctor, or nurse role
    
    Supported languages:
    - en-US: English
    - zh-CN: Mandarin (Simplified)
    - zh-HK: Cantonese
    - fr-FR: French
    - es-ES: Spanish
    
    Audio formats: mp3, wav, m4a, flac, ogg
    
    Process:
    1. Transcribe audio to text
    2. Translate to English if non-English (optional)
    3. Classify the incident
    """
    try:
        logger.info(f"Audio classification request from user: {current_user['username']}")
        
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
            start_time = time.time()
            
            # Transcribe and translate audio
            logger.info("Transcribing audio...")
            transcription_result = audio_service.transcribe_and_translate(
                tmp_path,
                language_code=language,
                auto_translate=auto_translate
            )
            
            # Get final transcript (translated if applicable)
            transcript = transcription_result["transcript"]
            
            if not transcript or len(transcript.strip()) < 10:
                raise HTTPException(
                    status_code=400,
                    detail="Transcription too short or empty. Please provide clearer audio."
                )
            
            logger.info(f"Transcript: {transcript[:100]}...")
            
            # Classify the incident
            logger.info("Classifying incident...")
            classification_result = classification_service.classify_incident(
                description=transcript,
                department=department
            )
            
            processing_time = time.time() - start_time
            
            logger.info(f"Audio classification complete in {processing_time:.2f}s")
            
            return AudioClassificationResponse(
                transcription={
                    "transcript": transcription_result["transcript"],
                    "original_language": transcription_result["original_language"],
                    "was_translated": transcription_result["was_translated"],
                    "confidence": transcription_result["confidence"],
                    "duration_seconds": transcription_result.get("duration_seconds")
                },
                classification=classification_result,
                processing_time=processing_time
            )
            
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio classification error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Audio classification failed: {str(e)}"
        )
