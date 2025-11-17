# Diretório Tests 🧪

Este diretório contém a suíte completa de testes que garante que todas as partes da aplicação funcionem correta e confiavelmente.

## 🎯 Propósito

O diretório `tests/` fornece testes abrangentes para todos os componentes da aplicação, ajudando a prevenir bugs, garantir segurança e manter qualidade de código durante desenvolvimento e deploy.

## 📁 Estrutura do Diretório

```
tests/
├── __init__.py                # Inicialização do pacote
├── conftest.py               # Configuração de teste compartilhada e fixtures
├── test_api.py               # Testes de integração de endpoints da API
├── test_auth_service.py      # Testes do serviço de autenticação
├── test_auth.py              # Testes de fluxo de autenticação
├── test_models.py            # Testes de validação de modelos de dados
├── test_password_service.py  # Testes de segurança de senhas
└── test_services.py          # Testes de serviços de lógica de negócio
```

## 📄 Visão Geral dos Arquivos

### `conftest.py` - Configuração de Testes
**Propósito**: Configuração de teste compartilhada e fixtures reutilizáveis

**O que faz**:
- Configura banco de dados de teste (separado da produção)
- Cria cliente de teste para testes da API
- Fornece dados de teste de amostra
- Configura configurações do ambiente de teste
- Gerencia limpeza do banco de dados de teste

**Para iniciantes**: Pense nisso como o "assistente de configuração de teste" que prepara tudo que é necessário para os testes rodarem adequadamente, como configurar um banco de dados de teste separado para que seus dados reais não sejam afetados.

### `test_api.py` - Testes de Integração da API
**Propósito**: Testa fluxos completos da API da requisição à resposta

**O que testa**:
- Endpoint de registro de usuário
- Endpoint de login de usuário
- Acesso a endpoints protegidos
- Tratamento de erros e códigos de status
- Formatos de dados de requisição/resposta

**Para iniciantes**: Estes testes verificam se os endpoints da sua API funcionam corretamente quando alguém faz requisições HTTP para eles, como testar se o botão "criar usuário" realmente cria um usuário.

### `test_auth_service.py` - Testes do Serviço de Autenticação
**Propósito**: Testa o sistema de autenticação e tokens JWT

**What it tests**:
- User authentication with valid/invalid credentials
- JWT token creation and validation
- Token expiration handling
- Token blacklisting (logout)
- Security edge cases

**For beginners**: These tests make sure the "login system" works correctly - that good passwords let people in and bad passwords keep them out.

### `test_auth.py` - Authentication Flow Tests
**Purpose**: Tests complete authentication workflows

**What it tests**:
- Full login/logout cycles
- Protected endpoint access with tokens
- Token refresh mechanisms
- Authentication error scenarios

### `test_models.py` - Data Validation Tests
**Purpose**: Tests Pydantic models for input/output validation

**What it tests**:
- Valid data acceptance
- Invalid data rejection
- Password strength requirements
- Username format validation
- Age and description constraints

**For beginners**: These tests make sure the "data checkers" work correctly - that invalid usernames, weak passwords, or impossible ages get rejected before they cause problems.

### `test_password_service.py` - Password Security Tests
**Purpose**: Tests password hashing and verification

**What it tests**:
- Password hashing produces different results each time
- Password verification works correctly
- Invalid passwords are rejected
- Security configurations work properly

**For beginners**: These tests make sure passwords are "scrambled" properly so hackers can't read them, but the system can still check if a password is correct.

### `test_services.py` - Business Logic Tests
**Purpose**: Tests all service layer business logic

**What it tests**:
- User creation, update, deletion
- Business rule enforcement
- Error handling
- Database operations
- Service integration

**For beginners**: These tests check that all the "business rules" work correctly - like making sure you can't create two users with the same username.

## 🧪 Types of Tests

### Unit Tests
Test individual functions in isolation:
```python
def test_hash_password():
    """Test that password hashing works correctly"""
    password = "TestPassword123!"
    hashed = hash_password(password)
    
    # Hash should be different from original
    assert hashed != password
    
    # Hash should be valid bcrypt format
    assert hashed.startswith("$2b$")
    
    # Should verify correctly
    assert verify_password(password, hashed) == True
```

### Integration Tests
Test how components work together:
```python
@pytest.mark.asyncio
async def test_user_creation_flow():
    """Test complete user creation process"""
    # 1. Create user via API
    response = client.post("/api/v1/users", json={
        "username": "testuser",
        "password": "TestPass123!",
        "age": 25
    })
    
    # 2. Check API response
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["username"] == "testuser"
    
    # 3. Verify user exists in database
    user = await get_user_by_username("testuser")
    assert user is not None
```

### API Tests
Test HTTP endpoints directly:
```python
def test_login_endpoint():
    """Test user login via API"""
    # Create user first
    client.post("/api/v1/users", json={
        "username": "logintest",
        "password": "LoginPass123!",
        "age": 30
    })
    
    # Test login
    response = client.post("/api/v1/auth/login", json={
        "username": "logintest", 
        "password": "LoginPass123!"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "user" in data
```

## 🏃‍♂️ Running Tests

### Run All Tests
```bash
# Run entire test suite
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=.

# Run with detailed coverage report
pytest --cov=. --cov-report=html
```

### Run Specific Tests
```bash
# Run specific test file
pytest tests/test_auth.py

# Run specific test function
pytest tests/test_auth.py::test_login_success

# Run tests matching pattern
pytest -k "password"

# Run only failed tests from last run
pytest --lf
```

### Run Tests by Category
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests  
pytest -m integration

# Run only slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

## 📊 Test Coverage

### Understanding Coverage
Coverage shows which lines of code are tested:

```bash
# Generate coverage report
pytest --cov=. --cov-report=term-missing

# Example output:
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
api/v1/auth_routes.py      45      2    96%   23, 67
services/auth_service.py   38      0   100%
services/user_service.py   52      5    90%   12-16
-----------------------------------------------------
TOTAL                     135      7    95%
```

### Coverage Goals
- **90%+ Overall**: Good test coverage
- **100% Critical Paths**: Authentication, security, data validation
- **80%+ Non-Critical**: Utilities, formatting, less critical features

## 🔧 Test Fixtures

### Database Fixtures
```python
# conftest.py
@pytest.fixture
async def test_db():
    """Provides clean test database for each test"""
    # Create test database
    await init_test_database()
    yield
    # Clean up after test
    await cleanup_test_database()

@pytest.fixture
async def sample_user():
    """Creates a sample user for testing"""
    user_data = {
        "username": "testuser",
        "password": hash_password("TestPass123!"),
        "age": 25,
        "description": "Test user"
    }
    return await create_user(user_data)
```

### API Client Fixtures
```python
@pytest.fixture
def client():
    """Provides test client for API testing"""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def authenticated_client(client, sample_user):
    """Provides authenticated test client"""
    # Login to get token
    response = client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "TestPass123!"
    })
    token = response.json()["token"]["access_token"]
    
    # Set authorization header
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
```

## 🛡️ Security Testing

### Authentication Tests
```python
def test_protected_endpoint_requires_auth(client):
    """Test that protected endpoints require authentication"""
    response = client.get("/api/v1/users/testuser")
    assert response.status_code == 401

def test_invalid_token_rejected(client):
    """Test that invalid tokens are rejected"""
    client.headers.update({"Authorization": "Bearer invalid_token"})
    response = client.get("/api/v1/users/testuser")
    assert response.status_code == 401
```

### Input Validation Tests
```python
def test_weak_password_rejected(client):
    """Test that weak passwords are rejected"""
    response = client.post("/api/v1/users", json={
        "username": "testuser",
        "password": "weak",  # Too weak
        "age": 25
    })
    assert response.status_code == 422
    assert "password" in response.json()["detail"][0]["loc"]

def test_invalid_username_rejected(client):
    """Test that invalid usernames are rejected"""  
    response = client.post("/api/v1/users", json={
        "username": "ab",  # Too short
        "password": "ValidPass123!",
        "age": 25
    })
    assert response.status_code == 422
```

### SQL Injection Tests
```python
def test_sql_injection_prevention():
    """Test that SQL injection attempts are prevented"""
    # Attempt SQL injection in username
    malicious_username = "'; DROP TABLE users; --"
    
    response = client.post("/api/v1/users", json={
        "username": malicious_username,
        "password": "ValidPass123!",
        "age": 25
    })
    
    # Should be rejected due to validation
    assert response.status_code == 422
```

## 🚀 Performance Testing

### Response Time Tests
```python
import time

def test_api_response_time(client):
    """Test that API responds within acceptable time"""
    start_time = time.time()
    
    response = client.get("/health")
    
    end_time = time.time()
    response_time = end_time - start_time
    
    assert response.status_code == 200
    assert response_time < 0.1  # Less than 100ms
```

### Load Testing
```python
@pytest.mark.slow
def test_concurrent_user_creation():
    """Test handling multiple concurrent requests"""
    import concurrent.futures
    
    def create_user(index):
        return client.post("/api/v1/users", json={
            "username": f"user{index}",
            "password": "TestPass123!",
            "age": 25
        })
    
    # Create 10 users concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(create_user, i) for i in range(10)]
        results = [future.result() for future in futures]
    
    # All should succeed
    assert all(r.status_code == 201 for r in results)
```

## 🐛 Debugging Tests

### Using pytest-pdb
```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb
```

### Adding Debug Output
```python
def test_user_creation_debug(client):
    response = client.post("/api/v1/users", json={
        "username": "debuguser",
        "password": "DebugPass123!",
        "age": 25
    })
    
    # Add debug output
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
    
    assert response.status_code == 201
```

### Capturing Logs in Tests
```python
import logging

def test_with_log_capture(caplog):
    with caplog.at_level(logging.INFO):
        # Code that logs something
        logger.info("Test log message")
    
    assert "Test log message" in caplog.text
```

## 🎓 Learning Path

**Beginner**: 
1. Run the existing tests and see what passes/fails
2. Read test function names to understand what they test
3. Look at simple unit tests first
4. Try modifying a test to see what happens

**Intermediate**: 
1. Write your own simple unit tests
2. Understand fixtures and test setup
3. Learn about mocking and test isolation
4. Study integration test patterns

**Advanced**: 
1. Write comprehensive test suites for new features
2. Set up continuous integration testing
3. Implement performance and load testing
4. Design test strategies for complex systems

## 🔄 Continuous Integration

### GitHub Actions Integration
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Now tests run automatically before each commit
```

---

**Next**: Check out the [`k8s/`](../k8s/README.md) directory to see how the application is deployed to Kubernetes!