# Testing Documentation

## Overview

This directory contains the complete test suite for the Safety Event Classification API. All tests run inside Docker containers for consistency across development and CI environments.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Shared pytest fixtures and configuration
├── unit/                 # Unit tests (44 tests)
│   ├── test_auth.py      # Password hashing, JWT tokens (14 tests)
│   ├── test_config.py    # Configuration settings (17 tests)
│   └── test_lang.py      # Language detection (13 tests)
├── integration/          # Integration tests (25 tests)
│   └── test_api.py       # Full API integration with TestClient
└── system/               # System tests (E2E)
    └── test_system_api.py # Complete system tests with real HTTP
```

**Total: 69 tests** (44 unit + 25 integration)

## Running Tests

### Prerequisites

- Docker installed and running
- Project root directory: `/Users/bruce/Desktop/APCOMP 215/AC215_888`

### Quick Start

```bash
# Build test container (from project root)
docker build -t safety-event-api:local -f Dockerfile.test .

# Run all tests
docker run --rm safety-event-api:local pytest tests/ -v

# Run with coverage
docker run --rm safety-event-api:local pytest tests/ \
  --cov=utils --cov=routers --cov=services --cov=models \
  --cov-report=term-missing
```

### Using the Test Script

```bash
# From project root
./run-tests.sh          # Run all tests
./run-tests.sh unit     # Run unit tests only
./run-tests.sh integration  # Run integration tests only
./run-tests.sh system   # Run system tests (requires API running)
./run-tests.sh coverage # Run with coverage report
./run-tests.sh build    # Rebuild Docker image
```

### Running Specific Tests

```bash
# Run specific test file
docker run --rm safety-event-api:local pytest tests/unit/test_auth.py -v

# Run specific test class
docker run --rm safety-event-api:local pytest tests/unit/test_auth.py::TestPasswordHashing -v

# Run specific test method
docker run --rm safety-event-api:local pytest tests/unit/test_auth.py::TestPasswordHashing::test_hash_password_returns_string -v

# Run tests matching pattern
docker run --rm safety-event-api:local pytest tests/ -k "auth" -v
```

## Test Types

### Unit Tests (44 tests)

**Characteristics:**
- Fast execution (<5 seconds total)
- No external dependencies
- Test individual functions/classes in isolation
- No network calls, no database, no LLM

**Coverage:**
- `test_auth.py` (14 tests):
  - Password hashing with bcrypt
  - Password verification
  - JWT token creation and validation
  - Token expiration handling
  - Edge cases (empty passwords, special characters, long passwords)

- `test_config.py` (17 tests):
  - Configuration loading from environment
  - Default values
  - Type validation
  - Department and language lists
  - GCP and LLM settings

- `test_lang.py` (13 tests):
  - Language detection for 7+ languages
  - Simplified vs Traditional Chinese distinction
  - Pseudo-translation formatting
  - Empty string handling
  - Mixed content detection

### Integration Tests (25 tests)

**Characteristics:**
- Use FastAPI TestClient (ASGI, no real HTTP)
- Test API endpoints and routing
- Mock external services (GCP, LLM)
- Test request/response schemas
- Execution time: ~5-10 seconds

**Coverage:**
- Root endpoints (4 tests): Welcome message, version, docs link
- Health endpoints (2 tests): v1 and legacy health checks
- Auth endpoints (5 tests): Login success/failure, JWT validation
- Translation endpoints (6 tests): Language detection, translation flow
- Classification endpoints (4 tests): Authentication, role-based access
- CORS (2 tests): Cross-origin configuration
- Error handling (2 tests): 404, 405 responses

**Key Features:**
- All Google Cloud services are mocked
- No credentials required
- Tests run without network access
- Validates API contracts and schemas

### System Tests (E2E)

**Characteristics:**
- Real HTTP requests to localhost:9000
- Requires API server running
- Tests complete end-to-end workflows
- Execution time: ~10-15 seconds

**Coverage:**
- API accessibility and response times
- Complete authentication flow
- Translation service integration
- Error handling across HTTP stack

**Running System Tests:**
```bash
# Terminal 1: Start API server
cd src/api
./docker-shell.sh
# Inside container: uvicorn_server

# Terminal 2: Run system tests
docker run --rm --network host safety-event-api:local pytest tests/system/ -v
```

## Coverage Metrics

### Current Coverage: 52%

| Module | Coverage | Notes |
|--------|----------|-------|
| **utils/** | **98%** | Fully tested, core utilities |
| utils/auth.py | 96% | Password hashing, JWT tokens |
| utils/config.py | 100% | Configuration settings |
| utils/lang.py | 100% | Language detection |
| utils/logger.py | 100% | Logging setup |
| **models/** | **91%** | Pydantic schemas |
| models/schemas.py | 91% | Excludes optional validators |
| **routers/** | **55%** | API endpoints |
| routers/auth.py | 88% | Login, logout, user profile |
| routers/translate.py | 79% | Translation endpoints |
| routers/speech.py | 89% | Speech recognition |
| routers/classification.py | 21% | Requires live LLM |
| routers/audio.py | 32% | Requires Google Speech API |
| routers/users.py | 21% | Database operations |
| **services/** | **36%** | Business logic |
| services/classification_service.py | 40% | LLM integration |
| services/rag_service.py | 46% | ChromaDB integration |
| services/audio_service.py | 22% | Audio processing |

### Why Some Modules Have Lower Coverage

**Classification Service (21-40%):**
- Requires live Vertex AI connection
- Complex multi-step classification logic
- Prompt engineering and response parsing
- Tested via integration tests with mocks

**Audio Service (22-32%):**
- Requires Google Speech API
- File upload and streaming
- Audio format conversions
- Tested via integration tests with mocks

**Users Service (21%):**
- Database operations not fully implemented
- User management features in development

**RAG Service (46%):**
- Requires ChromaDB connection
- Vector embeddings and similarity search
- Policy document retrieval
- Tested via integration tests with mocks

## CI/CD Integration

### GitHub Actions Workflow

The CI pipeline (`.github/workflows/ci.yml`) runs on every push and PR:

**Jobs:**
1. **Build** - Creates Docker image with all dependencies
2. **Lint and Format** - Black (formatting) and Flake8 (linting)
3. **Unit Tests** - 44 tests, ~5 seconds
4. **Integration Tests** - 25 tests, ~10 seconds
5. **System Tests** - E2E tests against running API
6. **Coverage Report** - Combined coverage with 50% minimum threshold
7. **Test Summary** - Summary of all test results

**Artifacts:**
- Docker image (shared across jobs)
- Coverage reports (XML, HTML)
- Test logs

**Coverage Threshold:**
- Minimum: 50%
- Current: 52% ✅
- Goal: 70%+

## Writing New Tests

### Unit Test Template

```python
"""
Unit tests for [module name]

Tests [functionality] in isolation.
No external dependencies required - fast execution.
"""

import pytest
from utils.my_module import my_function


class TestMyFunction:
    """Tests for my_function"""

    def test_basic_functionality(self):
        """Test basic case"""
        result = my_function("input")
        assert result == "expected"

    def test_edge_case(self):
        """Test edge case"""
        result = my_function("")
        assert result is None
```

### Integration Test Template

```python
"""
Integration tests for [API endpoint]

Tests the full API endpoint with FastAPI TestClient.
Mocks external services.
"""

import pytest
from fastapi.testclient import TestClient
from service import app

client = TestClient(app)


class TestMyEndpoint:
    """Integration tests for /api/v1/my-endpoint"""

    def test_success_case(self):
        """Test successful request"""
        response = client.post(
            "/api/v1/my-endpoint",
            json={"key": "value"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
```

## Best Practices

1. **Use descriptive test names** - Test name should explain what it tests
2. **One assertion per test** - Or closely related assertions
3. **Use fixtures for setup** - Define in `conftest.py` for reuse
4. **Mock external services** - No real API calls in tests
5. **Test edge cases** - Empty strings, None, invalid inputs
6. **Keep tests independent** - Tests should not depend on each other
7. **Use markers** - `@pytest.mark.unit`, `@pytest.mark.integration`

## Troubleshooting

### Tests Fail to Import Modules

```bash
# Rebuild Docker image
docker build -t safety-event-api:local -f Dockerfile.test .
```

### Coverage Not Generated

```bash
# Ensure coverage modules are installed
docker run --rm safety-event-api:local pip list | grep cov
```

### System Tests Fail

```bash
# Check if API is running
curl http://localhost:9000/api/v1/health

# Check API logs
docker logs api-container-name
```

### Integration Tests Timeout

```bash
# Check if mocks are properly configured in conftest.py
# Increase timeout in pytest.ini if needed
```

## What Remains Untested

### Critical Gaps (High Risk)

**1. LLM Classification Pipeline (79% untested)**
- ❌ Multi-step classification logic (GAPS → Patient Reach → Harm)
- ❌ Prompt engineering and template rendering
- ❌ LLM response parsing and validation
- ❌ Error handling for malformed LLM outputs
- ❌ Department-specific classification variations
- ❌ Fallback logic when LLM fails
- **Impact:** Core functionality, production-critical
- **Reason:** Requires live Vertex AI, non-deterministic responses
- **Workaround:** Tested manually, integration tests with mocks

### Moderate Gaps (Medium Risk)

**2. Audio Processing Service (68-78% untested)**
- ❌ Audio file upload validation (file size, format)
- ❌ Speech-to-text transcription with Google Speech API
- ❌ Multi-language audio processing
- ❌ Audio format conversions (mp3 → wav, etc.)
- ❌ Streaming audio handling
- ❌ Error recovery from transcription failures
- **Impact:** Optional feature, not main workflow
- **Reason:** Requires Google Speech API, audio fixtures (large files)
- **Workaround:** Integration tests with mocked API calls

**3. RAG Policy Retrieval (54% untested)**
- ❌ ChromaDB vector similarity search
- ❌ Policy document embedding generation
- ❌ Department-specific policy filtering
- ❌ Context augmentation in prompts
- ❌ Embedding cache management
- **Impact:** Enhancement feature, classification works without it
- **Reason:** Requires ChromaDB connection, pre-computed embeddings
- **Workaround:** Integration tests with mocked vector DB

**4. Batch Processing (Not tested)**
- ❌ CSV/Excel file parsing and validation
- ❌ Bulk classification job management
- ❌ Progress tracking for large batches
- ❌ Error handling in batch operations
- ❌ Results aggregation and export
- **Impact:** Useful for bulk operations, not critical path
- **Reason:** Complex file handling, not prioritized for MVP
- **Workaround:** Manual testing with sample files

**5. Performance and Scalability (Not tested)**
- ❌ Load testing (concurrent users)
- ❌ Response time under stress
- ❌ Memory usage with large inputs
- ❌ Rate limiting effectiveness
- ❌ Database connection pooling
- **Impact:** Affects production scalability
- **Reason:** Requires load testing infrastructure
- **Workaround:** K8s auto-scaling, production monitoring

### Minor Gaps (Low Risk)

**6. User Management Features (79% untested)**
- ❌ User creation and updates
- ❌ Role-based access control (beyond auth)
- ❌ User listing and filtering
- ❌ Password reset flow
- **Impact:** Admin features, not main workflow
- **Reason:** Database operations not fully implemented
- **Workaround:** Basic auth tested, admin features tested manually

**7. WebSocket Features (Not tested)**
- ❌ Real-time classification updates
- ❌ WebSocket connection management
- ❌ Live progress notifications
- **Impact:** Feature not deployed/used
- **Reason:** Not implemented in production
- **Workaround:** N/A - feature not active

**8. Edge Cases and Error Scenarios**
- ❌ Network timeouts and retry logic
- ❌ Concurrent request race conditions
- ❌ Large input handling (>10KB)
- ❌ Special character encoding edge cases
- ❌ API rate limit behavior
- **Impact:** Could cause production issues
- **Reason:** Difficult to simulate reliably
- **Workaround:** Error logging, production monitoring

### Summary by Risk Level

| Risk Level | Untested Functionality | Mitigation |
|------------|------------------------|------------|
| **High** | LLM classification pipeline | Integration tests with mocks, manual testing |
| **Medium** | Audio processing, RAG, batch processing, performance | Mocked integration tests, limited rollout |
| **Low** | User management, WebSocket, edge cases | Manual testing, production monitoring |

### Testing Challenges

**Why These Remain Untested:**

1. **External Service Dependencies**
   - Vertex AI LLM (paid, rate-limited)
   - Google Speech API (requires audio files)
   - ChromaDB (requires vector database setup)

2. **Non-Deterministic Behavior**
   - LLM outputs vary between runs
   - Difficult to assert on exact responses

3. **Infrastructure Requirements**
   - Load testing needs dedicated infrastructure
   - Database testing needs persistent storage
   - WebSocket testing needs connection management

4. **Time and Resource Constraints**
   - MVP focused on core functionality
   - Complex features deferred to later sprints

### Mitigation Strategies

✅ **What We Do Instead:**

1. **Integration Tests with Mocks** - Cover basic flows without external APIs
2. **Manual Testing** - Critical paths tested by team before deployment
3. **Production Monitoring** - CloudWatch/GCP logs for runtime errors
4. **Gradual Rollout** - Limited user base initially
5. **Error Logging** - Comprehensive logging for debugging
6. **K8s Auto-scaling** - Handles unexpected load
7. **Health Checks** - Continuous monitoring of service availability

## Future Improvements

### Short-term (Next Sprint)
- [ ] Add LLM classification tests with recorded fixtures
- [ ] Add audio transcription tests with sample audio files
- [ ] Add RAG service tests with mock embeddings
- [ ] Add batch processing endpoint tests

### Medium-term (Next Milestone)
- [ ] Increase coverage to 70%+
- [ ] Add performance/load tests
- [ ] Add security tests (penetration, auth bypass)
- [ ] Add database tests when user management is complete

### Long-term (Production)
- [ ] Add contract tests for frontend integration
- [ ] Add chaos engineering tests
- [ ] Add compliance tests (HIPAA)
- [ ] Add end-to-end UI tests

## References

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Project Testing Guide](../README.md#testing)
