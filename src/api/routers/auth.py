"""
Authentication API Router

User authentication endpoints with JWT token management.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timedelta
from typing import Dict, Any

from models.schemas import (
    UserLogin,
    TokenResponse,
    PasswordResetRequest,
    PasswordReset
)
from utils.auth import hash_password, verify_password, create_access_token, require_role
from utils.logger import logger
from utils.config import settings

router = APIRouter()

# In-memory user storage (replace with database in production)
users_db: Dict[str, Dict[str, Any]] = {
    "admin": {
        "username": "admin",
        "email": "admin@hospital.com",
        "password_hash": hash_password("admin123"),
        "role": "admin",
        "department": "internal medicine",
        "created_at": datetime.utcnow().isoformat()
    }
}

# Password reset tokens (replace with Redis/database in production)
reset_tokens: Dict[str, Dict[str, Any]] = {}


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login"
)
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
        # Get user
        user = users_db.get(credentials.username)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        
        # Update last login
        user["last_login"] = datetime.utcnow().isoformat()
        
        logger.info(f"User logged in: {credentials.username}")
        
        # Create access token
        token_data = {
            "username": user["username"],
            "role": user["role"],
            "email": user["email"],
            "department": user.get("department")
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
                "department": user.get("department")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Login failed"
        )


@router.post(
    "/forgot-password",
    summary="Request password reset"
)
async def forgot_password(request: PasswordResetRequest):
    """
    Request password reset token
    
    Request body:
    ```json
    {
        "username": "jdoe",
        "email": "jdoe@hospital.com"
    }
    ```
    
    In production, this would send an email with reset link.
    For development, returns the token in response.
    """
    try:
        # Find user
        user = users_db.get(request.username)
        
        if not user or user["email"] != request.email:
            # Don't reveal if user exists
            return {
                "message": "If the credentials are correct, a reset token has been generated",
                "dev_note": "Invalid credentials" if not user or user["email"] != request.email else None
            }
        
        # Generate reset token
        import secrets
        reset_token = secrets.token_urlsafe(32)
        
        reset_tokens[reset_token] = {
            "username": request.username,
            "expires": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        logger.info(f"Password reset requested for: {request.username}")
        
        # In production, send email here
        # For development, return token
        return {
            "message": "Password reset token generated",
            "dev_token": reset_token,  # Remove in production
            "dev_note": "In production, this token would be emailed to the user"
        }
        
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Password reset failed"
        )


@router.post(
    "/reset-password",
    summary="Reset password with token"
)
async def reset_password(reset_data: PasswordReset):
    """
    Reset password using reset token
    
    Request body:
    ```json
    {
        "token": "reset_token_here",
        "new_password": "newpassword123"
    }
    ```
    """
    try:
        # Validate token
        if reset_data.token not in reset_tokens:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired reset token"
            )
        
        token_info = reset_tokens[reset_data.token]
        
        # Check expiration
        expires = datetime.fromisoformat(token_info["expires"])
        if datetime.utcnow() > expires:
            del reset_tokens[reset_data.token]
            raise HTTPException(
                status_code=400,
                detail="Reset token has expired"
            )
        
        # Update password
        username = token_info["username"]
        if username in users_db:
            users_db[username]["password_hash"] = hash_password(reset_data.new_password)
            del reset_tokens[reset_data.token]
            
            logger.info(f"Password reset successful for: {username}")
            
            return {
                "message": "Password reset successfully",
                "username": username
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Password reset failed"
        )


@router.get(
    "/verify",
    summary="Verify JWT token"
)
async def verify_token(current_user: Dict = Depends(require_role("admin", "doctor", "nurse", "viewer"))):
    """
    Verify if the provided JWT token is valid
    
    Requires: Authorization header with Bearer token
    
    Returns user information if token is valid
    """
    return {
        "valid": True,
        "user": current_user
    }
