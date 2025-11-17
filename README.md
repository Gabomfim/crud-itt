# crud-itt

[![CI/CD Pipeline](https://github.com/Gabomfim/crud-itt/actions/workflows/ci.yml/badge.svg)](https://github.com/Gabomfim/crud-itt/actions/workflows/ci.yml)
[![Deploy to Staging](https://github.com/Gabomfim/crud-itt/actions/workflows/deploy-staging.yml/badge.svg)](https://github.com/Gabomfim/crud-itt/actions/workflows/deploy-staging.yml)
[![Deploy to Production](https://github.com/Gabomfim/crud-itt/actions/workflows/deploy-production.yml/badge.svg)](https://github.com/Gabomfim/crud-itt/actions/workflows/deploy-production.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# CRUD ITT - User Management API

A comprehensive FastAPI application with full user management capabilities, authentication, and security features.

## 🚀 Project Overview

This is a production-ready REST API built with FastAPI that provides complete user management functionality including:

- **User Registration & Authentication** - Secure user accounts with JWT tokens
- **Password Management** - Secure password hashing and change functionality  
- **User CRUD Operations** - Create, Read, Update, Delete users
- **Security Features** - JWT authentication, password validation, rate limiting
- **Database Integration** - Async SQLAlchemy with multiple database support
- **Production Ready** - Logging, monitoring, Docker support, Kubernetes deployment

## 📁 Project Structure

```
crud-itt/
├── api/                    # API endpoints and routes
├── config/                 # Application configuration
├── database/               # Database connections and models
├── models/                 # Data models and validation
├── services/               # Business logic layer
├── utils/                  # Utility functions and middleware
├── static/                 # Static files (CSS, images)
├── templates/              # HTML templates
├── tests/                  # Test suite
├── k8s/                    # Kubernetes deployment files
├── scripts/                # Utility scripts
├── backup/                 # Backup configurations
├── app.py                  # Main application entry point
└── requirements files      # Python dependencies
```

## 🏁 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL or SQLite (for database)
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd crud-itt
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize the database**
   ```bash
   python -m database.init
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 🔑 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Register** a new user: `POST /api/v1/users`
2. **Login** to get token: `POST /api/v1/auth/login`  
3. **Use token** in headers: `Authorization: Bearer <your-token>`

## 🗂️ Directory Guide

Each directory contains a detailed README explaining its purpose:

- [`api/`](api/README.md) - API endpoints and routing
- [`config/`](config/README.md) - Configuration management
- [`database/`](database/README.md) - Database connections and ORM
- [`models/`](models/README.md) - Data validation models
- [`services/`](services/README.md) - Business logic layer
- [`utils/`](utils/README.md) - Utilities and middleware
- [`tests/`](tests/README.md) - Test suite
- [`k8s/`](k8s/README.md) - Kubernetes deployment
- [`static/`](static/README.md) - Static web assets
- [`templates/`](templates/README.md) - HTML templates
- [`scripts/`](scripts/README.md) - Utility scripts

## 🛠️ Key Features

### Security
- ✅ JWT token authentication
- ✅ Bcrypt password hashing
- ✅ Input validation and sanitization
- ✅ SQL injection prevention
- ✅ CORS configuration
- ✅ Rate limiting ready

### Performance
- ✅ Async/await throughout
- ✅ Database connection pooling
- ✅ Efficient query patterns
- ✅ Request/response caching
- ✅ Structured logging

### Development
- ✅ Comprehensive test suite
- ✅ Docker containerization
- ✅ Kubernetes deployment
- ✅ Environment-based configuration
- ✅ Code documentation
- ✅ Type hints throughout

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.

# Run specific test file
python -m pytest tests/test_auth.py
```

## 🐳 Docker Deployment

Build and run with Docker:
```bash
# Build image
docker build -t crud-itt .

# Run container
docker run -p 8000:8000 crud-itt

# Or use docker-compose
docker-compose up
```

## ☸️ Kubernetes Deployment

Deploy to Kubernetes:
```bash
# Apply all configurations
kubectl apply -k k8s/

# Check deployment status
kubectl get pods -n crud-itt
```

## 📝 Environment Configuration

Key environment variables:

```bash
# Application
APP_NAME=CRUD ITT
APP_ENVIRONMENT=development
APP_DEBUG=false

# Database
DATABASE_URL=sqlite+aiosqlite:///./database/users.db

# Security
JWT_SECRET_KEY=your-secret-key-here
SECURITY_SECRET_KEY=your-app-secret-here

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

## 🚀 Deployment Workflows

This project includes automated deployment workflows for staging and production environments:

### Staging Deployment
- **Trigger**: Push to `staging` branch
- **Environment**: `crud-itt-staging` namespace
- **Features**: 
  - Automated testing
  - Docker image build and push
  - Kubernetes deployment
  - Health checks
  - Slack notifications

### Production Deployment  
- **Trigger**: Push to `main` branch
- **Environment**: `crud-itt` namespace
- **Features**:
  - Comprehensive testing and security scanning
  - Staging environment verification
  - Blue-green deployment
  - Automatic rollback on failure
  - Health checks and smoke tests
  - Multi-level notifications

### Manual Deployment
Both workflows support manual triggering with additional options:
- `force_deploy`: Skip tests and deploy anyway
- `skip_staging_check`: (Production only) Skip staging verification

## 📋 Deployment Requirements

Before using the deployment workflows, ensure you have:

1. **GitHub Secrets configured** (see [DEPLOYMENT.md](DEPLOYMENT.md))
2. **Kubernetes clusters** set up for staging and production
3. **Container registry** access (GitHub Container Registry)
4. **Database** instances configured for each environment

For detailed setup instructions, see the [Deployment Guide](DEPLOYMENT.md).

## 🔧 Environment Configuration

The application uses Pydantic settings for type-safe environment variable management:

```python
from config import settings

# Application settings
print(f"App: {settings.app.name} v{settings.app.version}")
print(f"Environment: {settings.app.environment}")

# Database settings  
print(f"Database URL: {settings.database.url}")

# Security settings
print(f"BCrypt rounds: {settings.security.bcrypt_rounds}")
```

See `config/settings.py` for all available configuration options.

## 📊 Health Monitoring

The application includes built-in health monitoring:

- **Health Endpoint**: `GET /health`
- **Kubernetes Probes**: Liveness and readiness checks
- **Logging**: Structured logging with configurable levels
- **Metrics**: Integration-ready for monitoring tools

## 🔐 Security Features

- **Password Security**: Configurable complexity requirements
- **BCrypt Hashing**: Environment-specific round counts
- **Secret Management**: Kubernetes secrets integration
- **Container Security**: Non-root user, minimal privileges
- **Vulnerability Scanning**: Automated Trivy scans in CI/CD

## 📚 API Endpoints

### Authentication

- **POST** `/api/v1/auth/login` - Login and receive JWT token
- **POST** `/api/v1/auth/logout` - Logout and blacklist token  
- **GET** `/api/v1/auth/me` - Get current user information

#### Login Request
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

#### Login Response
```json
{
  "user": {
    "id": 1,
    "username": "your_username",
    "age": 25,
    "description": "User description"
  },
  "token": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "message": "Login successful"
}
```

### User Management (🔒 Authentication Required)

- **GET** `/api/v1/users/{username}` - Get user information
- **GET** `/api/v1/users?minimum_age={age}` - Get users by minimum age
- **POST** `/api/v1/users` - Create a new user (⚠️ Public endpoint)
- **PUT** `/api/v1/users/{username}` - Update user information
- **DELETE** `/api/v1/users/{username}` - Delete a user

### Password Management (🔒 Authentication Required)

- **PUT** `/api/v1/users/{username}/password` - Change user password

#### Change Password Request
```json
{
  "current_password": "current_password",
  "new_password": "new_secure_password",
  "confirm_password": "new_secure_password"
}
```

**Requirements:**
- Current password must be correct
- New password must meet complexity requirements (configurable)
- New password must be different from current password
- Password confirmation must match new password

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

### Authentication Headers

For protected endpoints, include the JWT token in the Authorization header:

```bash
Authorization: Bearer your_jwt_token_here
```

### Example Usage

```bash
# 1. Login to get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "TestPassword123!"}'

# 2. Use token for protected endpoints
curl -X GET "http://localhost:8000/api/v1/users/testuser" \
  -H "Authorization: Bearer your_jwt_token_here"

# 3. Logout to blacklist token
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer your_jwt_token_here"
```
