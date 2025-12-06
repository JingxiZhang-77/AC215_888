# Archive Log

This directory contains obsolete files and folders that are no longer used in the current project architecture.

## Archived Items (November 24, 2025)

### src/model-original/
**Original Location:** `src/model/`  
**Reason:** The model directory has been copied into `src/api/model/` to support building the API Docker image from the api directory context. The API service now uses the local copy at `src/api/model/` which contains `simple_prompt_utils.py` and related prompt utilities.  
**Dependencies:** None - the API uses its own local copy  

### src/frontend-legacy/
**Original Location:** `src/frontend-legacy/`  
**Reason:** Replaced by the new React-based frontend at `src/frontend-react/`. The legacy frontend used Flask templates and is no longer maintained.  
**Technology Stack:** Flask, Jinja2 templates, vanilla JavaScript  
**Replacement:** Next.js 15 with React 18, Tailwind CSS  

### src/audio-service/
**Original Location:** `src/audio-service/`  
**Reason:** Audio transcription functionality has been integrated directly into the API service at `src/api/services/audio_service.py`. The standalone audio service is no longer needed.  
**Functionality:** Google Cloud Speech-to-Text with multi-language support  
**Replacement:** `src/api/services/audio_service.py` with integrated audio transcription  

### src/RAG/
**Original Location:** `src/RAG/`  
**Reason:** Experimental RAG (Retrieval-Augmented Generation) implementation that was not integrated into the main application. Contains semantic chunking and RAG prototypes.  
**Status:** Experimental code, not used in production  

### Screenshot Files
**Files:** `sc1.png`, `sc2.png`  
**Reason:** Old screenshot files that are no longer referenced in documentation  

## Previously Archived Items

### docker-compose.yml
**Date:** November 21, 2025  
**Reason:** Old docker-compose configuration replaced by individual docker-shell.sh scripts  

### Dockerfile.api
**Date:** November 21, 2025  
**Reason:** Old API Dockerfile configuration  

### TRANSLATION_SETUP.md
**Date:** November 21, 2025  
**Reason:** Old translation setup documentation  

### guildline_RAG.py
**Date:** October 14, 2024  
**Reason:** RAG guideline prototype  

### web/
**Date:** November 21, 2025  
**Reason:** Old web frontend files  

---

## Current Project Structure

After archiving, the active project structure is:

```
src/
├── api/                    # FastAPI backend service
│   ├── model/             # Local copy of prompt utilities
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic (includes audio service)
│   ├── models/            # Pydantic schemas
│   ├── utils/             # Utilities
│   └── service.py         # FastAPI application entry point
├── frontend-react/        # Next.js frontend (active)
└── datapipeline/          # Data generation utilities
```

## Restoration Instructions

If you need to restore any archived item:

1. Locate the item in this `_archive/` directory
2. Copy (don't move) it back to its original location
3. Update any import statements or references as needed
4. Test thoroughly before committing

**Note:** For `model-original/`, use the copy at `src/api/model/` instead of restoring the original.

## Maintenance Notes

- Keep this archive directory for reference but do not include it in production builds
- Consider removing items older than 6 months after verification they're not needed
- Update this log when adding new archived items
