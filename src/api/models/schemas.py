"""
Data Models for Safety Event Classification API

Pydantic models for request/response validation and documentation.
Following PEP 8 style guide with comprehensive docstrings.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class DepartmentEnum(str, Enum):
    """Valid medical departments"""
    INTERNAL_MEDICINE = "internal medicine"
    SURGERY = "surgery"
    OB_GYN_NICU = "ob/gyn/nicu"
    RADIOLOGY_IMAGING = "radiology/imaging"
    OUTPATIENT_ER = "outpatient/ER"

    @staticmethod
    def _normalize_value(value: str) -> str:
        """Normalize department strings for matching"""
        if not isinstance(value, str):
            return ""
        normalized = value.strip().lower()
        for char in ['_', '-', '/']:
            normalized = normalized.replace(char, ' ')
        return ' '.join(normalized.split())

    @classmethod
    def _missing_(cls, value):
        """
        Allow alternate department spellings (e.g., internal_medicine)
        by normalizing incoming values before matching Enum members.
        """
        normalized = cls._normalize_value(value)
        for member in cls:
            if cls._normalize_value(member.value) == normalized:
                return member
        return None


class LanguageEnum(str, Enum):
    """Supported languages for audio transcription"""
    ENGLISH = "en-US"
    MANDARIN = "zh-CN"
    CANTONESE = "zh-HK"
    FRENCH = "fr-FR"
    SPANISH = "es-ES"


class UserRole(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    VIEWER = "viewer"


# ============ Authentication Models ============

class UserLogin(BaseModel):
    """User login request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class UserRegister(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=8)
    role: UserRole = Field(default=UserRole.VIEWER)
    department: Optional[DepartmentEnum] = Field(default=None)


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    username: str
    email: str


class PasswordReset(BaseModel):
    """Password reset with token"""
    token: str
    new_password: str = Field(..., min_length=8)


# ============ Classification Models ============

class ClassificationRequest(BaseModel):
    """Single incident classification request"""
    description: str = Field(..., min_length=10, max_length=5000)
    department: Optional[DepartmentEnum] = None

    @validator('description')
    def validate_description(cls, v):
        """Ensure description is not empty after stripping"""
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()


class ClassificationResult(BaseModel):
    """Classification result with rationales"""
    incident: str
    department: str
    department_label: Optional[str] = None
    department_slug: Optional[str] = None
    deviation_check: str
    deviation_rationale: str
    patient_reach_check: str
    patient_reach_rationale: str
    harm_level_check: str
    harm_level_rationale: str
    classification_code: str
    classification_label: str
    classification_rationale: str
    status: str
    timestamp: Optional[datetime] = None
    # Legacy fields for backward compatibility
    gaps_deviation_check: Optional[str] = None
    gaps_rationale: Optional[str] = None
    reached_patient_check: Optional[str] = None
    reached_patient_rationale: Optional[str] = None
    final_classification_code: Optional[str] = None
    final_rationale: Optional[str] = None


class BatchClassificationResponse(BaseModel):
    """Batch classification response"""
    total_incidents: int = Field(description="Total number of incidents processed")
    successful: int = Field(description="Number of successfully classified incidents")
    failed: int = Field(description="Number of failed classifications")
    processing_time: float = Field(description="Total processing time in seconds")
    summary: Dict[str, int] = Field(description="Classification code breakdown")
    results_file: str = Field(description="CSV content of results")
    output_filename: str = Field(description="Suggested filename for download")
    results: Optional[List[ClassificationResult]] = Field(default=None, description="Detailed results (optional)")


# ============ Audio Models ============

class AudioTranscriptionRequest(BaseModel):
    """Audio transcription request (multipart/form-data)"""
    language: Optional[LanguageEnum] = Field(
        default=LanguageEnum.ENGLISH,
        description="Language of audio file"
    )
    auto_translate: bool = Field(
        default=True,
        description="Automatically translate to English if non-English"
    )


class AudioTranscriptionResponse(BaseModel):
    """Audio transcription response"""
    transcript: str
    original_language: str
    was_translated: bool
    confidence: float
    duration_seconds: Optional[float] = None


class AudioClassificationRequest(BaseModel):
    """Audio classification request with transcription"""
    language: Optional[LanguageEnum] = Field(default=LanguageEnum.ENGLISH)
    department: Optional[DepartmentEnum] = None
    auto_translate: bool = Field(default=True)


class AudioClassificationResponse(BaseModel):
    """Audio classification response"""
    transcription: AudioTranscriptionResponse
    classification: ClassificationResult
    processing_time: float


# ============ User Management Models ============

class UserInfo(BaseModel):
    """User information response"""
    username: str
    email: str
    role: UserRole
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserUpdate(BaseModel):
    """User update request (admin only)"""
    role: Optional[UserRole] = None
    email: Optional[str] = None


class UserListResponse(BaseModel):
    """List of users response"""
    users: List[UserInfo]
    count: int


# ============ Error Models ============

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    status_code: int


class ValidationError(BaseModel):
    """Validation error details"""
    field: str
    message: str
    type: str
