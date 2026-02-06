# Testing Guide

This document provides comprehensive guidance on testing the FastAPI Boilerplate application, including setup, conventions, and best practices for writing production-grade tests.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Fixtures](#fixtures)
- [Mocking Strategy](#mocking-strategy)
- [Test Categories](#test-categories)
- [Best Practices](#best-practices)
- [Coverage Reports](#coverage-reports)
- [Continuous Integration](#continuous-integration)

---

## Overview

The testing framework is built on:

- **pytest** - Python's most popular testing framework
- **pytest-asyncio** - Async test support for FastAPI endpoints
- **pytest-cov** - Code coverage reporting
- **httpx** - Async HTTP client for testing FastAPI applications
- **unittest.mock** - Mocking utilities for isolating tests

### Testing Philosophy

1. **Unit Tests First** - Focus on isolated, fast tests that verify individual components
2. **Mock External Dependencies** - Database, cache, email services are mocked in unit tests
3. **Test Behavior, Not Implementation** - Tests verify what the code does, not how it does it
4. **Clear Test Names** - Tests are self-documenting through descriptive names
5. **AAA Pattern** - Arrange, Act, Assert structure in all tests

---

## Quick Start

### 1. Install Test Dependencies

```bash
pip install -r requirements.txt
```

Or install testing packages individually:

```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

### 2. Run All Tests

```bash
pytest
```

### 3. Run Tests with Coverage

```bash
pytest --cov=app --cov-report=term-missing
```

### 4. Run Specific Test Module

```bash
pytest tests/unit/api/v1/test_auth.py -v
```

---

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests (no external deps)
│   ├── __init__.py
│   ├── api/                 # API endpoint tests
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── test_auth.py
│   │       ├── test_user.py       # (future)
│   │       ├── test_role.py       # (future)
│   │       └── test_profile.py    # (future)
│   └── services/            # Service layer tests (future)
│       ├── __init__.py
│       ├── test_auth_service.py
│       └── test_user_service.py
├── integration/             # Integration tests (future)
│   ├── __init__.py
│   └── test_database.py
└── e2e/                     # End-to-end tests (future)
    ├── __init__.py
    └── test_auth_flow.py
```

### Directory Purposes

| Directory | Purpose | Dependencies |
|-----------|---------|--------------|
| `unit/` | Fast, isolated tests | Mocked only |
| `unit/api/` | HTTP endpoint tests | Mocked services |
| `unit/services/` | Business logic tests | Mocked repos |
| `integration/` | Tests with real DB | Database |
| `e2e/` | Full flow tests | All services |

---

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/api/v1/test_auth.py

# Run specific test class
pytest tests/unit/api/v1/test_auth.py::TestLoginEndpoint

# Run specific test
pytest tests/unit/api/v1/test_auth.py::TestLoginEndpoint::test_login_success

# Run tests matching pattern
pytest -k "login"

# Run marked tests only
pytest -m "unit"
pytest -m "not slow"
```

### Parallel Execution

Install pytest-xdist for parallel execution:

```bash
pip install pytest-xdist
pytest -n auto  # Uses all CPU cores
pytest -n 4     # Uses 4 workers
```

### Watch Mode

Use pytest-watch for automatic re-running:

```bash
pip install pytest-watch
ptw  # Watches and re-runs on changes
```

---

## Writing Tests

### Test File Structure

```python
"""
Module docstring explaining what tests cover.
"""

import pytest
from unittest.mock import MagicMock

# Constants
API_PREFIX = "/api/v1/auth"


class TestLoginEndpoint:
    """Test cases for the login endpoint."""
    
    endpoint = f"{API_PREFIX}/login"
    
    def test_login_success(
        self,
        client,
        container_with_mocked_auth_service,
        mock_auth_service,
        valid_login_data,
        sample_auth_response
    ):
        """
        Test successful login with valid credentials.
        
        Given: Valid email and password
        When: POST /api/v1/auth/login is called
        Then: Return 200 with auth response
        """
        # Arrange
        mock_auth_service.login.return_value = sample_auth_response
        
        # Act
        response = client.post(self.endpoint, json=valid_login_data)
        
        # Assert
        assert response.status_code == 200
        assert "tokenInfo" in response.json()
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Test files | `test_*.py` | `test_auth.py` |
| Test classes | `Test*` | `TestLoginEndpoint` |
| Test functions | `test_*` | `test_login_success` |
| Fixtures | descriptive | `sample_auth_response` |

### Test Function Naming Pattern

```
test_<action>_<scenario>_<expected_outcome>
```

Examples:
- `test_login_success` - Happy path
- `test_login_invalid_email_format` - Validation error
- `test_login_user_not_found` - Business logic error
- `test_login_inactive_account` - Edge case

---

## Fixtures

Fixtures are defined in `tests/conftest.py` and provide reusable test data and mocks.

### Application Fixtures

```python
# Test client for making HTTP requests
@pytest.fixture
def client(app) -> TestClient:
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

# Async client for async tests
@pytest.fixture
async def async_client(app) -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as ac:
        yield ac
```

### Mock Service Fixtures

```python
@pytest.fixture
def mock_auth_service() -> MagicMock:
    """Create a mock auth service with async methods."""
    mock = MagicMock()
    mock.login = AsyncMock()
    mock.refresh_token = AsyncMock()
    mock.forgot_password = AsyncMock()
    mock.reset_password = AsyncMock()
    return mock
```

### Sample Data Fixtures

```python
@pytest.fixture
def sample_auth_response(sample_token_response, sample_user_response):
    """Complete auth response for testing."""
    return AuthResponse(
        tokenInfo=sample_token_response,
        userInfo=sample_user_response
    )

@pytest.fixture
def valid_login_data() -> dict:
    """Valid login request data."""
    return {
        "email": "test@example.com",
        "password": "pass123"
    }
```

### Container Override Fixtures

```python
@pytest.fixture
def container_with_mocked_auth_service(app, mock_auth_service):
    """Override container with mocked auth service."""
    container = app.container
    with container.auth_service.override(mock_auth_service):
        yield container
```

### Available Fixtures

| Fixture | Description |
|---------|-------------|
| `app` | FastAPI application instance |
| `client` | Synchronous test client |
| `async_client` | Asynchronous test client |
| `mock_auth_service` | Mocked auth service |
| `mock_user_service` | Mocked user service |
| `mock_token_service` | Mocked token service |
| `mock_user_repository` | Mocked user repository |
| `sample_user` | Sample User model |
| `sample_auth_response` | Sample AuthResponse |
| `valid_login_data` | Valid login request |
| `container_with_mocked_auth_service` | Container with mocked auth |

---

## Mocking Strategy

### Dependency Injection Overrides

The application uses dependency-injector for DI. Tests override services at the container level:

```python
@pytest.fixture
def container_with_mocked_auth_service(app, mock_auth_service):
    container = app.container
    with container.auth_service.override(mock_auth_service):
        yield container
```

### Configuring Mock Returns

```python
# Success case
mock_auth_service.login.return_value = sample_auth_response

# Error case
mock_auth_service.login.side_effect = NotFoundException(
    key="email",
    message="User not found"
)

# Verify calls
mock_auth_service.login.assert_called_once_with("email", "password")
mock_auth_service.login.assert_not_called()
```

### Async Mocks

For async methods, use `AsyncMock`:

```python
from unittest.mock import AsyncMock

mock = MagicMock()
mock.login = AsyncMock(return_value=sample_auth_response)
```

---

## Test Categories

### Unit Tests (Current)

Fast tests with fully mocked dependencies:

```python
@pytest.mark.unit
def test_login_success(self, client, ...):
    ...
```

### Integration Tests (Future)

Tests that interact with a real database:

```python
@pytest.mark.integration
async def test_create_user_in_database(db_session, ...):
    ...
```

### Slow Tests

Tests that take longer to run:

```python
@pytest.mark.slow
def test_heavy_computation(self):
    ...
```

### Running by Category

```bash
pytest -m "unit"
pytest -m "not slow"
pytest -m "integration"
```

---

## Best Practices

### 1. Arrange-Act-Assert Pattern

```python
def test_example(self, client, mock_service):
    # Arrange - Set up test data and mocks
    mock_service.method.return_value = expected_value
    
    # Act - Execute the code being tested
    response = client.post("/endpoint", json=data)
    
    # Assert - Verify the results
    assert response.status_code == 200
    assert response.json()["key"] == expected_value
```

### 2. One Assertion Concept Per Test

```python
# Good - Single concept
def test_login_returns_access_token(self, ...):
    response = client.post("/login", json=data)
    assert "access_token" in response.json()["tokenInfo"]

# Avoid - Multiple unrelated assertions
def test_login(self, ...):
    response = client.post("/login", json=data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.headers["Content-Type"] == "application/json"
    assert mock_service.method.called
```

### 3. Test Edge Cases

```python
class TestLoginEdgeCases:
    def test_login_with_special_characters_in_email(self, ...):
        login_data = {"email": "test+alias@example.com", "password": "pass123"}
        response = client.post("/login", json=login_data)
        assert response.status_code == 200
    
    def test_login_with_unicode_password(self, ...):
        login_data = {"email": "test@example.com", "password": "päss123"}
        response = client.post("/login", json=login_data)
        assert response.status_code == 200
```

### 4. Use Descriptive Docstrings

```python
def test_login_success(self, ...):
    """
    Test successful login with valid credentials.
    
    Given: Valid email and password
    When: POST /api/v1/auth/login is called
    Then: Return 200 with auth response containing tokens and user info
    """
```

### 5. Don't Test Implementation Details

```python
# Good - Test behavior
def test_login_returns_tokens(self, ...):
    response = client.post("/login", json=data)
    assert "access_token" in response.json()["tokenInfo"]

# Avoid - Testing internal implementation
def test_login_calls_repository(self, ...):
    response = client.post("/login", json=data)
    mock_repository.get_by_email.assert_called_once()
```

---

## Coverage Reports

### Generate Terminal Report

```bash
pytest --cov=app --cov-report=term-missing
```

### Generate HTML Report

```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### Coverage Configuration

In `pytest.ini`:

```ini
[pytest]
addopts = --cov=app --cov-report=term-missing --cov-report=html

# Minimum coverage threshold
# --cov-fail-under=80
```

### Exclude Files from Coverage

In `.coveragerc`:

```ini
[run]
omit = 
    tests/*
    app/core/migrations/*
    app/main.py
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml -v
    
    - name: Upload coverage
      uses: codecov/codecov-action@v4
      with:
        files: coverage.xml
```

---

## Troubleshooting

### Common Issues

**1. Async test not running**

Ensure `asyncio_mode = auto` in pytest.ini and tests are marked properly:

```python
@pytest.mark.asyncio
async def test_async_endpoint(async_client):
    response = await async_client.get("/endpoint")
```

**2. Container override not working**

Make sure to use the fixture in your test:

```python
def test_something(
    self,
    client,
    container_with_mocked_auth_service,  # Must include this!
    mock_auth_service
):
    ...
```

**3. Import errors**

Ensure the project root is in PYTHONPATH:

```bash
PYTHONPATH=. pytest
```

**4. Database connection errors in unit tests**

Unit tests should not connect to the database. Use mocks:

```python
# In conftest.py
@pytest.fixture(autouse=True)
def mock_database():
    with patch("app.core.database.session.async_session"):
        yield
```

---

## Future Test Modules

The following test modules will be added:

| Module | Status | Description |
|--------|--------|-------------|
| `test_auth.py` | ✅ Complete | Authentication endpoints |
| `test_user.py` | 🔜 Planned | User management endpoints |
| `test_role.py` | 🔜 Planned | Role management endpoints |  
| `test_profile.py` | 🔜 Planned | Profile endpoints |
| `test_auth_service.py` | 🔜 Planned | Auth service unit tests |
| `test_user_service.py` | 🔜 Planned | User service unit tests |

---

## Summary

This testing framework provides:

- ✅ Production-grade pytest configuration
- ✅ Comprehensive fixtures for mocking
- ✅ Clear test organization
- ✅ Full coverage of auth endpoints
- ✅ Documentation for extending tests

For questions or contributions, please refer to the project's contribution guidelines.
