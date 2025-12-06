# API Archive

This folder contains legacy/redundant files that have been removed from the active codebase.

## Archived Files

### `classify_dummy.py` (originally `routers/classify.py`)
- **Date Archived:** November 21, 2025
- **Reason:** Legacy dummy router with hardcoded mock responses
- **Replacement:** `routers/classification.py` is the production router with full AI classification logic
- **Status:** Not imported anywhere in the codebase
- **Description:** 
  - Contained a single `/classify` endpoint with placeholder logic
  - Used `dummy_chain()` function that returned fake "PSE" or "NSE" codes
  - Did not integrate with actual ML models or `simple_prompt_utils`

## Active Routers (Not Archived)

The following routers are actively used and should NOT be archived:

- **`classification.py`**: Main production router (single, batch, audio classification)
- **`audio.py`**: Audio transcription endpoints (used by frontend)
- **`auth.py`**: Authentication endpoints (login, register, password reset)
- **`users.py`**: User management (admin CRUD operations)
- **`translate.py`**: Translation endpoint (used by frontend `/translate` page)
- **`speech.py`**: Stub endpoint (minimal, but explicitly imported in main.py)

## Restoration

If you need to restore any archived file:

```bash
# From src/api directory
cp _archive/classify_dummy.py routers/classify.py
```

---

**Note:** Before restoring, verify the file is actually needed and won't conflict with current implementations.
