# Docker Entrypoint Setup

## Overview
Both the `datapipeline` and `model` folders now include `docker-entrypoint.sh` scripts following the pattern from the lecture tutorials. This provides a cleaner and more maintainable Docker container initialization process.

## What Changed

### Files Created
1. **`src/datapipeline/docker-entrypoint.sh`**
   - Activates the virtual environment automatically
   - Displays welcome message with system info
   - Shows available Python scripts
   - Provides usage examples

2. **`src/model/docker-entrypoint.sh`**
   - Activates the virtual environment automatically
   - Displays welcome message with system info
   - Shows available Python scripts
   - Provides usage examples

### Files Modified
1. **`src/datapipeline/Dockerfile`**
   - Added `chmod +x docker-entrypoint.sh` to make script executable
   - Changed `ENTRYPOINT` to use `docker-entrypoint.sh`
   - Removed inline CMD with activation logic

2. **`src/model/Dockerfile`**
   - Added `chmod +x docker-entrypoint.sh` to make script executable
   - Changed `ENTRYPOINT` to use `docker-entrypoint.sh`
   - Removed inline CMD with activation logic

## Benefits

### Before (Old Approach)
```dockerfile
ENTRYPOINT ["/bin/bash"]
CMD ["-c", "source /home/app/.venv/bin/activate && exec bash"]
```
- Virtual environment activation mixed in Dockerfile
- No welcome messages or helpful information
- Harder to customize startup behavior

### After (New Approach)
```dockerfile
ENTRYPOINT ["/bin/bash", "docker-entrypoint.sh"]
```
- Clean separation of concerns
- Easy to modify startup behavior without rebuilding
- Provides helpful context when container starts
- Matches industry best practices and lecture tutorials

## Usage

### Data Pipeline Container
```bash
cd src/datapipeline
./docker-shell.sh
```

You'll see:
```
Container is running!!!
Architecture: x86_64
Activating virtual environment...
Environment ready! Virtual environment activated.
Python version: Python 3.11.x
UV version: uv x.x.x

===================================
Data Pipeline Environment Ready
===================================
Available Python scripts:
  - data_generation.py

Example usage:
  python data_generation.py
```

### Model Container
```bash
cd src/model
./docker-shell.sh
```

You'll see:
```
Container is running!!!
Architecture: x86_64
Activating virtual environment...
Environment ready! Virtual environment activated.
Python version: Python 3.11.x
UV version: uv x.x.x

===================================
Model Environment Ready
===================================
Available Python scripts:
  - safety_event_classifier.py
  - prompt_utils.py
  - simple_prompt_utils.py

Example usage:
  python safety_event_classifier.py
```

## Customization

You can easily customize the entrypoint scripts to:
- Add more environment variables
- Run initialization commands
- Set up additional services
- Display custom welcome messages
- Run health checks

Simply edit `docker-entrypoint.sh` and the changes take effect on next container start (no rebuild needed if volumes are mounted).

## Pattern Reference

This implementation follows the pattern from:
- `references/lecture_tutorials/llm-rag/docker-entrypoint.sh`
- `references/lecture_tutorials/llm-rag/Dockerfile`

The pattern ensures:
- Virtual environment is always activated
- User gets helpful feedback on container start
- Easy debugging with version information
- Consistent across all project containers
