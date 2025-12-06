"""
Authentication API Router

User authentication endpoints with JWT token management.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timedelta
from typing import Dict, Any

from models.schemas import UserLogin, TokenResponse
from utils.auth import hash_password, verify_password, create_access_token, require_role
from utils.logger import logger
from utils.config import settings

router = APIRouter()

# In-memory user storage (replace with database in production)
# Lazy initialization to avoid hashing at import time
users_db: Dict[str, Dict[str, Any]] = {}


def _initialize_default_users():
    """Initialize default users on first access"""
    if not users_db:
        users_db["admin"] = {
            "username": "admin",
            "email": "admin@hospital.com",
            "password_hash": hash_password("admin123"),
            "role": "admin",
            "department": "internal medicine",
            "created_at": datetime.utcnow().isoformat(),
        }


@router.post("/login", response_model=TokenResponse, summary="User login")
async def login(credentials: UserLogin):
    """
    Authenticate user and return JWT token

    Request body:
    ```json
    {
        "username": "admin",
        "password": "admin123"
    }
    ```
    """
    try:
        # Initialize default users on first access
        _initialize_default_users()

        # Get user
        user = users_db.get(credentials.username)

        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Verify password
        if not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Update last login
        user["last_login"] = datetime.utcnow().isoformat()

        logger.info(f"User logged in: {credentials.username}")

        # Create access token
        token_data = {
            "username": user["username"],
            "role": user["role"],
            "email": user["email"],
            "department": user.get("department"),
        }
        access_token = create_access_token(token_data)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRATION_HOURS * 3600,
            user={
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "department": user.get("department"),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.get("/verify", summary="Verify JWT token")
async def verify_token(current_user: Dict = Depends(require_role("admin", "doctor", "nurse", "viewer"))):
    """
    Verify if the provided JWT token is valid

    Requires: Authorization header with Bearer token

    Returns user information if token is valid
    """
    return {"valid": True, "user": current_user}
