# Safety Event Classification API - Test Suite

This directory contains the automated test suite for the Safety Event Classification API, following the CI/CD patterns from the cheese-app-ci-cd reference.

## Test Structure

```
tests/
├── pytest.ini              # Pytest configuration
├── conftest.py             # Shared fixtures
├── run-tests.sh            # Local test runner script
├── unit/                   # Unit tests
│   ├── test_lang.py        # Language detection tests
│   ├── test_auth.py        # Authentication utilities tests
│   └── test_config.py      # Configuration tests
├── integration/            # Integration tests
│   └── test_api.py         # API endpoint tests (TestClient)
└── system/                 # System/E2E tests
    └── test_system_api.py  # Real HTTP request tests
```

## Test Types

### Unit Tests (`tests/unit/`)
- Test utility functions in isolation
- No external dependencies
- Fast execution
- Run inside Docker container

**Examples:**
- `test_lang.py` - Language detection (Chinese, Spanish, French, etc.)
- `test_auth.py` - Password hashing, JWT token creation/validation
- `test_config.py` - Configuration settings validation

### Integration Tests (`tests/integration/`)
- Use FastAPI's TestClient
- Test API endpoints with routing, validation, response schemas
- No real HTTP server required
- Run inside Docker container

**Coverage:**
- Root endpoints (`/`, `/health`)
- Authentication (`/api/v1/auth/login`)
- Translation (`/api/v1/translate`)
- Classification (`/api/v1/classify/`)
- CORS configuration
- OpenAPI documentation

### System Tests (`tests/system/`)
- End-to-end tests against fully running system
- Real HTTP requests to `localhost:9000`
- Test the entire HTTP stack
- Run with `--network host` in Docker

**Requirements:**
- API server running at `http://localhost:9000`
- Can be run in CI/CD after starting the server container

## Running Tests Locally

### Prerequisites
```bash
cd src/api
uv sync --dev
```

### Using the Test Script
```bash
# Run unit tests only
./run-tests.sh unit

# Run integration tests
./run-tests.sh integration

# Run system tests (requires running API)
./run-tests.sh system

# Run all tests (unit + integration)
./run-tests.sh all

# Run with coverage report
./run-tests.sh coverage
```

### Using pytest directly
```bash
cd src/api

# Run all unit tests
pytest tests/unit/ -v

# Run all integration tests
pytest tests/integration/ -v

# Run with coverage
pytest tests/unit/ tests/integration/ \
    --cov=utils --cov=routers --cov=services \
    --cov-report=term-missing \
    --cov-fail-under=50
```

### Running System Tests
```bash
# 1. Start the API server
cd src/api
./docker-shell.sh
# Inside container:
uvicorn service:app --host 0.0.0.0 --port 9000

# 2. In another terminal, run system tests
cd src/tests
pytest system/ -v
```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs:

1. **Build** - Build Docker image
2. **Lint and Format** - Run Flake8 linter
3. **Unit Tests** - Run unit tests with coverage
4. **Integration Tests** - Run integration tests with TestClient
5. **System Tests** - Start API server, run E2E tests
6. **Coverage Report** - Generate combined coverage report
7. **Test Summary** - Display results summary

## Coverage Target

The project aims for **≥50% code coverage**.

Coverage is measured on:
- `utils/` - Utility modules
- `routers/` - API endpoints
- `services/` - Business logic
- `models/` - Data models

## Test Markers

```python
@pytest.mark.unit          # Unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.system        # System tests
@pytest.mark.slow          # Slow-running tests
```

## Adding New Tests

1. **Unit Tests**: Add to `tests/unit/test_<module>.py`
   - Test one function/class in isolation
   - Mock external dependencies
   - Keep tests fast

2. **Integration Tests**: Add to `tests/integration/test_api.py`
   - Use `TestClient` from FastAPI
   - Test request/response cycles
   - Verify API contracts

3. **System Tests**: Add to `tests/system/test_system_api.py`
   - Use `requests` library
   - Test against running server
   - Include `@pytest.mark.skipif` for CI flexibility

## Troubleshooting

### Import Errors
Tests add `src/api` to `sys.path` for imports. If you see import errors:
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
```

### System Tests Skipped
If system tests are skipped, ensure:
- API is running at `http://localhost:9000`
- Run `curl http://localhost:9000/api/v1/health` to verify

### Coverage Not Meeting Target
Focus on testing:
- Utility functions (high value, low complexity)
- API endpoints (critical paths)
- Business logic in services
