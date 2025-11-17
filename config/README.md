# Diretório Configuration ⚙️

Este diretório contém toda a configuração da aplicação e gerenciamento de configurações.

## 🎯 Propósito

O diretório `config/` gerencia como a aplicação se comporta em diferentes ambientes (desenvolvimento, teste, produção) através de variáveis de ambiente e configurações.

## 📁 Estrutura do Diretório

```
config/
├── __init__.py          # Inicialização do pacote + exportação de configurações
└── settings.py          # Gerenciamento principal de configuração
```

## 📄 Visão Geral dos Arquivos

### `settings.py` - Gerenciamento de Configuração
**Propósito**: Sistema central de configuração para toda a aplicação

**O que faz**:
- Carrega configurações de variáveis de ambiente
- Fornece valores padrão para todas as configurações
- Valida valores de configuração
- Organiza configurações em categorias lógicas
- Torna configuração disponível em toda a app

**Para iniciantes**: Pense nisso como o "painel de controle" da sua app. Ele diz à aplicação como se comportar, onde encontrar o banco de dados, quais configurações de segurança usar, etc.

## 🏗️ Categorias de Configuração

### 1. Configurações da Aplicação
```python
app_name = "CRUD ITT"                    # App name
app_version = "1.0.0"                    # Version number
app_environment = "development"           # Environment type
app_debug = False                        # Debug mode on/off
```

### 2. Database Settings
```python
database_url = "sqlite+aiosqlite:///./database/users.db"  # Database connection
database_echo = False                    # Log SQL queries
database_pool_size = 10                  # Connection pool size
database_max_overflow = 20               # Max extra connections
```

### 3. Security Settings
```python
security_secret_key = "your-secret-key"     # App secret key
security_bcrypt_rounds = 12                 # Password hashing strength
security_password_min_length = 8            # Min password length
security_password_require_uppercase = True   # Password rules
```

### 4. JWT Token Settings
```python
jwt_secret_key = "your-jwt-secret"          # JWT signing key
jwt_algorithm = "HS256"                     # JWT algorithm
jwt_access_token_expire_minutes = 30        # Token expiry time
```

### 5. Server Settings
```python
server_host = "0.0.0.0"                    # Server host
server_port = 8000                         # Server port
server_workers = 1                         # Worker processes
server_reload = False                      # Auto-reload on changes
```

### 6. CORS Settings
```python
cors_origins = ["*"]                       # Allowed origins
cors_methods = ["GET", "POST", "PUT", "DELETE"]  # Allowed methods
cors_headers = ["*"]                       # Allowed headers
```

## 🌍 Environment Variables

You can override any setting using environment variables:

### Setting Environment Variables

**On Linux/Mac:**
```bash
export APP_NAME="My Custom App"
export DATABASE_URL="postgresql://user:pass@localhost/mydb"
export JWT_SECRET_KEY="my-super-secret-key"
```

**On Windows:**
```cmd
set APP_NAME=My Custom App
set DATABASE_URL=postgresql://user:pass@localhost/mydb
set JWT_SECRET_KEY=my-super-secret-key
```

**Using .env file:**
```bash
# Create .env file in project root
APP_NAME=My Custom App
DATABASE_URL=postgresql://user:pass@localhost/mydb
JWT_SECRET_KEY=my-super-secret-key
```

## 🏷️ Environment Types

### Development Environment
```bash
APP_ENVIRONMENT=development
APP_DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_ECHO=true    # Shows SQL queries
```

**Best for**: Local development, debugging, testing new features

### Testing Environment
```bash
APP_ENVIRONMENT=testing
APP_DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL=sqlite+aiosqlite:///:memory:  # In-memory database
```

**Best for**: Running automated tests, CI/CD pipelines

### Production Environment
```bash
APP_ENVIRONMENT=production
APP_DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://...  # Real database
JWT_SECRET_KEY=very-secure-key
```

**Best for**: Live application serving real users

## 🔧 How to Use Settings

### In Your Code
```python
from config import settings

# Access any setting
app_name = settings.app.name
db_url = settings.database.url
secret_key = settings.security.secret_key

# Check environment
if settings.is_development():
    print("Running in development mode")

if settings.is_production():
    print("Running in production mode")
```

### Getting Settings Instance
```python
from config import get_settings

# Get cached settings (recommended)
settings = get_settings()
```

## 🛡️ Security Best Practices

### ⚠️ Never Commit Secrets
```bash
# ❌ DON'T DO THIS
JWT_SECRET_KEY = "my-secret-key"  # Hard-coded in code

# ✅ DO THIS INSTEAD
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-for-dev")
```

### 🔐 Use Strong Secrets
```bash
# ❌ Weak secrets
JWT_SECRET_KEY=123456
SECURITY_SECRET_KEY=password

# ✅ Strong secrets (32+ characters)
JWT_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
SECURITY_SECRET_KEY=MyVerySecureAndLongSecretKeyForProduction2024
```

### 🎯 Environment-Specific Secrets
```bash
# Development
JWT_SECRET_KEY=dev-secret-key-not-for-production

# Production  
JWT_SECRET_KEY=prod-very-secure-key-32-chars-min
```

## 📝 Configuration Examples

### Local Development Setup
```bash
# .env file for development
APP_ENVIRONMENT=development
APP_DEBUG=true
DATABASE_URL=sqlite+aiosqlite:///./dev.db
LOG_LEVEL=DEBUG
JWT_SECRET_KEY=dev-secret-key
SECURITY_BCRYPT_ROUNDS=10
```

### Docker Production Setup
```bash
# .env file for production
APP_ENVIRONMENT=production
APP_DEBUG=false
DATABASE_URL=postgresql://user:pass@db:5432/crud_itt
LOG_LEVEL=INFO
JWT_SECRET_KEY=${JWT_SECRET_FROM_VAULT}
SECURITY_BCRYPT_ROUNDS=13
SERVER_WORKERS=4
```

## 🔍 Validation Features

### Automatic Type Conversion
```python
# Environment: SERVER_PORT=8080
settings.server.port  # Returns integer 8080, not string "8080"

# Environment: APP_DEBUG=true  
settings.app.debug    # Returns boolean True, not string "true"
```

### Enum Validation
```python
# Environment: APP_ENVIRONMENT=staging
settings.app.environment  # Returns Environment.STAGING enum

# Environment: LOG_LEVEL=ERROR
settings.log.level        # Returns LogLevel.ERROR enum
```

### Default Values
```python
# If JWT_ACCESS_TOKEN_EXPIRE_MINUTES is not set
settings.jwt.access_token_expire_minutes  # Returns default: 30
```

## 🧩 Integration with Other Components

### Database Connection
```python
# database/connection.py uses settings
engine = create_async_engine(
    settings.database.url,
    echo=settings.database.echo,
    pool_size=settings.database.pool_size
)
```

### Authentication Service
```python
# services/auth_service.py uses settings
def create_access_token(data: dict):
    return jwt.encode(
        data, 
        settings.jwt.secret_key,
        algorithm=settings.jwt.algorithm
    )
```

### FastAPI App
```python
# app.py uses settings
app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    debug=settings.app.debug
)
```

## 🎓 Learning Path

**Beginner**: 
1. Understand what each setting category does
2. Try changing settings with environment variables
3. See how settings affect app behavior

**Intermediate**: 
1. Study the validation and type conversion features
2. Learn about environment-specific configurations
3. Practice with different deployment scenarios

**Advanced**: 
1. Understand the caching mechanism (`@lru_cache`)
2. Learn about custom validation patterns
3. Study integration with external configuration systems

---

**Next**: Check out the [`database/`](../database/README.md) directory to see how database connections work!