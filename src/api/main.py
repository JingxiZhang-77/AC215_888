"""
Safety Event Classification API

FastAPI backend service providing REST APIs for:
- Safety event classification with AI-powered decision rationales
- Audio transcription with multi-language support and auto-translation
- Batch processing of incidents from CSV/Excel files
- User authentication and role-based access control
- Department-specific incident tracking

Author: AC215_888 Team
Date: January 2025
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routers import classification, audio, auth, users
from utils.config import settings
from utils.logger import logger

# Initialize FastAPI app
app = FastAPI(
    title="Safety Event Classification API",
    description="AI-powered safety event classification and analysis system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["User Management"])
app.include_router(classification.router, prefix="/api/v1/classify", tags=["Classification"])
app.include_router(audio.router, prefix="/api/v1/audio", tags=["Audio Transcription"])

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Safety Event Classification API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/api/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "safety-event-api",
        "version": "1.0.0"
    }

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Safety Event Classification API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Version: 1.0.0")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Safety Event Classification API")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
