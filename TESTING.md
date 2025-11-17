# Guia de Testes

## Visão Geral
Esta aplicação inclui testes abrangentes cobrindo:
- **Modelos**: Testes de validação Pydantic
- **Endpoints da API**: Testes de rotas FastAPI  
- **Serviços**: Testes de lógica de negócio
- **Integração**: Funcionalidade end-to-end

## Estrutura dos Testes
```
tests/
├── __init__.py          # Pacote de testes
├── conftest.py          # Configuração de testes e fixtures
├── test_models.py       # Testes de modelos Pydantic
├── test_api.py          # Testes de endpoints da API
└── test_services.py     # Testes da camada de serviço
```

## Executando Testes

### Instalar Dependências de Teste
```bash
pip install -r requirements.txt
```

### Executar Todos os Testes
```bash
pytest
```

### Executar Arquivos de Teste Específicos
```bash
pytest tests/test_models.py     # Testes de validação de modelos
pytest tests/test_api.py        # Testes de endpoints da API
pytest tests/test_services.py   # Testes da camada de serviço
```

### Executar com Saída Verbosa
```bash
pytest -v
```

### Executar com Cobertura
```bash
pip install pytest-cov
pytest --cov=. --cov-report=html
```

## Gerenciamento de Avisos do Pytest

### Visão Geral da Configuração

A configuração do pytest é definida em `pyproject.toml` com gerenciamento abrangente de avisos:

```toml
[tool.pytest.ini_options]
filterwarnings = [
    "error::DeprecationWarning",                    # Tratar avisos de depreciação como erros
    "error::PendingDeprecationWarning",             # Tratar avisos de depreciação pendente como erros
    "ignore::DeprecationWarning:pkg_resources.*",   # Ignorar depreciações pkg_resources
    "ignore::DeprecationWarning:distutils.*",       # Ignorar depreciações distutils
    "ignore::DeprecationWarning:urllib3.*",         # Ignorar depreciações urllib3
    "ignore::UserWarning:anyio.*",                  # Ignorar avisos de usuário anyio
    "ignore::RuntimeWarning:asyncio.*"              # Ignorar avisos de runtime asyncio
]
asyncio_mode = "auto"                               # Tratar testes async automaticamente
```

### Histórico de Resolução de Avisos

#### Migração Pydantic V2 ✅
- **Problema**: Avisos `PydanticDeprecatedSince20` para config baseada em classe
- **Solução**: Atualizado `models/responses.py` para usar `ConfigDict`:
  ```python
  # Antigo (depreciado)
  class Config:
      from_attributes = True
  
  # Novo (compatível com V2)  
  model_config = ConfigDict(from_attributes=True)
  ```

#### Configuração de Teste Async ✅
- **Problema**: Avisos Asyncio e problemas de execução de teste
- **Solução**: Adicionado `asyncio_mode = "auto"` para tratamento automático de async

### Executando Testes com Diferentes Níveis de Avisos

```bash
# Desenvolvimento (mostrar avisos)
pytest -W default

# CI/CD (avisos rigorosos)
pytest -W error::DeprecationWarning -W error::PendingDeprecationWarning

# Debug avisos específicos
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