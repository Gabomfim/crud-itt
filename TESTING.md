# Testing Guide

## Overview
This application includes comprehensive tests covering:
- **Models**: Pydantic validation testing
- **API Endpoints**: FastAPI route testing  
- **Services**: Business logic testing
- **Integration**: End-to-end functionality

## Test Structure
```
tests/
├── __init__.py          # Test package
├── conftest.py          # Test configuration & fixtures
├── test_models.py       # Pydantic model tests
├── test_api.py          # API endpoint tests
└── test_services.py     # Service layer tests
```

## Running Tests

### Install Test Dependencies
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run Specific Test Files
```bash
pytest tests/test_models.py     # Model validation tests
pytest tests/test_api.py        # API endpoint tests
pytest tests/test_services.py   # Service layer tests
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage
```bash
pip install pytest-cov
pytest --cov=. --cov-report=html
```

## Pytest Warning Management

### Configuration Overview

The pytest configuration is defined in `pyproject.toml` with comprehensive warning management:

```toml
[tool.pytest.ini_options]
filterwarnings = [
    "error::DeprecationWarning",                    # Treat deprecation warnings as errors
    "error::PendingDeprecationWarning",             # Treat pending deprecation warnings as errors
    "ignore::DeprecationWarning:pkg_resources.*",   # Ignore pkg_resources deprecations
    "ignore::DeprecationWarning:distutils.*",       # Ignore distutils deprecations
    "ignore::DeprecationWarning:urllib3.*",         # Ignore urllib3 deprecations
    "ignore::UserWarning:anyio.*",                  # Ignore anyio user warnings
    "ignore::RuntimeWarning:asyncio.*"              # Ignore asyncio runtime warnings
]
asyncio_mode = "auto"                               # Auto-handle async tests
```

### Warning Resolution History

#### Pydantic V2 Migration ✅
- **Issue**: `PydanticDeprecatedSince20` warnings for class-based config
- **Solution**: Updated `models/responses.py` to use `ConfigDict`:
  ```python
  # Old (deprecated)
  class Config:
      from_attributes = True
  
  # New (V2 compatible)  
  model_config = ConfigDict(from_attributes=True)
  ```

#### Async Test Configuration ✅
- **Issue**: Asyncio warnings and test execution issues
- **Solution**: Added `asyncio_mode = "auto"` for automatic async handling

### Running Tests with Different Warning Levels

```bash
# Development (show warnings)
pytest -W default

# CI/CD (strict warnings)
pytest -W error::DeprecationWarning -W error::PendingDeprecationWarning

# Debug specific warnings
pytest -W error::DeprecationWarning:my_module.*
```

## Test Categories

### 1. Model Tests (`test_models.py`)
- **UserRequest validation**: Username, password complexity, age, description
- **UserResponse validation**: Field constraints and configuration
- **Error handling**: Invalid data scenarios

### 2. API Tests (`test_api.py`)
- **CRUD operations**: Create, read, update, delete users
- **HTTP status codes**: 200, 201, 204, 400, 404, 422
- **Error responses**: Validation errors, not found, duplicates
- **HTML pages**: Root page and 404 error page

### 3. Service Tests (`test_services.py`)
- **Business logic**: User creation, retrieval, updates, deletion
- **Database operations**: SQLAlchemy ORM interactions
- **Exception handling**: HTTP exceptions and error cases

## Test Features

### Test Database
- Uses in-memory SQLite for isolation
- Fresh database for each test
- No impact on production data

### Fixtures
- `client`: FastAPI test client
- `sample_user`: Valid user data for testing

### Test Coverage
- **Password validation**: All complexity rules
- **Username validation**: Length, pattern matching
- **Age validation**: Range checking (1-120)
- **Description validation**: Length limits
- **API endpoints**: All CRUD operations
- **Error scenarios**: Invalid data, not found, duplicates

## Example Test Run
```bash
$ pytest -v
========================= test session starts =========================
tests/test_api.py::TestUserAPI::test_create_user_success PASSED
tests/test_api.py::TestUserAPI::test_get_user_success PASSED
tests/test_models.py::TestUserRequest::test_password_complexity_validation PASSED
tests/test_services.py::TestUserService::test_create_new_user_success PASSED
========================= 24 passed in 2.45s =========================
```

## Best Practices
1. **Isolation**: Each test is independent
2. **Clean Database**: Fresh state for every test
3. **Comprehensive Coverage**: All major code paths tested
4. **Clear Assertions**: Specific checks for expected behavior
5. **Error Testing**: Both success and failure scenarios