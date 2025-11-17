# Scripts Directory 🔧

This directory contains utility scripts for automating development, deployment, and maintenance tasks for the CRUD ITT application.

## 🎯 Purpose

The `scripts/` directory houses automation scripts that help developers streamline common tasks like setting up development environments, running deployments, and maintaining code quality.

## 📁 Directory Structure

```
scripts/
└── setup-pre-commit.sh    # Pre-commit hooks setup script
```

## 📄 File Overview

### `setup-pre-commit.sh` - Pre-commit Hooks Setup
**Purpose**: Automates the installation and configuration of pre-commit hooks for code quality

**What it does**:
- Installs pre-commit package if not already installed
- Sets up Git hooks to run automatically before commits
- Configures code formatting, linting, and security checks
- Ensures consistent code quality across all commits

**For beginners**: Think of this as a "quality control robot" that automatically checks your code before you save changes to Git. It catches common mistakes, formats your code nicely, and ensures everyone on the team follows the same coding standards.

## 🚀 Script Usage

### Running the Pre-commit Setup
```bash
# Make the script executable (first time only)
chmod +x scripts/setup-pre-commit.sh

# Run the setup script
./scripts/setup-pre-commit.sh

# Or run from project root
cd /path/to/crud-itt
bash scripts/setup-pre-commit.sh
```

### Manual Pre-commit Management
```bash
# Install pre-commit hooks manually
pip install pre-commit

# Install hooks for this repository
pre-commit install

# Run hooks on all files (bypass Git)
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate

# Uninstall hooks (if needed)
pre-commit uninstall
```

## ⚙️ Pre-commit Configuration

### Example `.pre-commit-config.yaml`
```yaml
# .pre-commit-config.yaml (in project root)
repos:
  # Code formatting
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3

  # Import sorting
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  # Code linting
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [
          "--max-line-length=88",
          "--extend-ignore=E203,W503"
        ]

  # Security scanning
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.4
    hooks:
      - id: bandit
        args: ["-r", ".", "-f", "json"]
        exclude: ^tests/

  # Type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  # General hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: debug-statements
      - id: requirements-txt-fixer
```

## 🔧 Additional Utility Scripts

### Development Environment Setup
```bash
#!/bin/bash
# scripts/setup-dev.sh

echo "🚀 Setting up CRUD ITT development environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
./scripts/setup-pre-commit.sh

# Create .env file from template
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file - please update with your settings"
fi

# Initialize database
python -c "from database.init import init_db; init_db()"

echo "✅ Development environment setup complete!"
```

### Database Management Scripts
```bash
#!/bin/bash
# scripts/db-backup.sh

# Database backup script
DB_NAME="crud_itt"
BACKUP_DIR="backup"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql"

echo "📦 Creating database backup..."

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create database backup
pg_dump "$DB_NAME" > "$BACKUP_FILE"

echo "✅ Database backup created: $BACKUP_FILE"

# Clean up old backups (keep last 7 days)
find "$BACKUP_DIR" -name "db_backup_*.sql" -mtime +7 -delete
```

### Code Quality Check Script
```bash
#!/bin/bash
# scripts/quality-check.sh

echo "🔍 Running code quality checks..."

# Exit on first error
set -e

# Run tests
echo "Running tests..."
python -m pytest tests/ -v --cov=. --cov-report=html

# Type checking
echo "Type checking..."
python -m mypy .

# Security scanning
echo "Security scanning..."
python -m bandit -r . -f json -o bandit-report.json

# Code formatting check
echo "Checking code formatting..."
python -m black --check .

# Import sorting check
echo "Checking import sorting..."
python -m isort --check-only .

# Linting
echo "Linting code..."
python -m flake8 .

echo "✅ All quality checks passed!"
```

### Docker Management Scripts
```bash
#!/bin/bash
# scripts/docker-dev.sh

# Docker development environment management

case "$1" in
    "build")
        echo "🏗️ Building Docker image..."
        docker build -t crud-itt:dev .
        ;;
    "run")
        echo "🚀 Starting Docker container..."
        docker run -d \
            --name crud-itt-dev \
            -p 8000:8000 \
            -v $(pwd):/app \
            -e ENV=development \
            crud-itt:dev
        ;;
    "stop")
        echo "🛑 Stopping Docker container..."
        docker stop crud-itt-dev
        docker rm crud-itt-dev
        ;;
    "logs")
        echo "📋 Showing Docker logs..."
        docker logs -f crud-itt-dev
        ;;
    "shell")
        echo "🐚 Opening shell in container..."
        docker exec -it crud-itt-dev /bin/bash
        ;;
    *)
        echo "Usage: $0 {build|run|stop|logs|shell}"
        exit 1
        ;;
esac
```

### Performance Testing Script
```bash
#!/bin/bash
# scripts/performance-test.sh

echo "⚡ Running performance tests..."

# Start the application in background
uvicorn app:app --host 0.0.0.0 --port 8000 --reload &
APP_PID=$!

# Wait for app to start
sleep 5

# Run load tests with different scenarios
echo "Testing user registration endpoint..."
ab -n 1000 -c 10 -p tests/data/register.json -T application/json http://localhost:8000/api/v1/auth/register

echo "Testing user login endpoint..."
ab -n 1000 -c 10 -p tests/data/login.json -T application/json http://localhost:8000/api/v1/auth/login

echo "Testing user profile endpoint..."
ab -n 1000 -c 10 -H "Authorization: Bearer your-test-token" http://localhost:8000/api/v1/users/profile

# Stop the application
kill $APP_PID

echo "✅ Performance tests completed!"
```

## 🎯 Script Best Practices

### Error Handling
```bash
#!/bin/bash
# scripts/example-with-error-handling.sh

# Exit on any error
set -e

# Function to handle errors
handle_error() {
    echo "❌ Error occurred in script at line $1"
    exit 1
}

# Trap errors
trap 'handle_error $LINENO' ERR

# Script logic here...
echo "🚀 Starting process..."

# Check if required files exist
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    exit 1
fi

echo "✅ Script completed successfully!"
```

### Logging and Output
```bash
#!/bin/bash
# scripts/example-with-logging.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  INFO: $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ SUCCESS: $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}"
}

log_error() {
    echo -e "${RED}❌ ERROR: $1${NC}"
}

# Usage examples
log_info "Starting deployment process..."
log_success "Database connection established"
log_warning "Using default configuration"
log_error "Failed to connect to external service"
```

### Configuration Management
```bash
#!/bin/bash
# scripts/config-example.sh

# Load configuration from file
CONFIG_FILE=".env"

if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
    echo "✅ Configuration loaded from $CONFIG_FILE"
else
    echo "⚠️  Configuration file not found, using defaults"
    DATABASE_URL="postgresql://localhost/crud_itt"
    SECRET_KEY="default-secret-key"
fi

# Validate required variables
required_vars=("DATABASE_URL" "SECRET_KEY")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set"
        exit 1
    fi
done

echo "✅ All required configuration variables are set"
```

## 🔒 Security Considerations

### Secure Script Practices
```bash
#!/bin/bash
# scripts/secure-example.sh

# Set secure permissions
umask 077

# Don't log sensitive commands
set +x

# Use secure temporary files
TEMP_FILE=$(mktemp)
trap "rm -f $TEMP_FILE" EXIT

# Validate input parameters
if [[ ! "$1" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "❌ Invalid parameter format"
    exit 1
fi

# Don't expose sensitive data in process list
export SECRET_KEY="$SECRET_KEY"
unset SECRET_KEY

echo "✅ Security practices applied"
```

### Credential Management
```bash
#!/bin/bash
# scripts/credential-example.sh

# Never hardcode credentials
# Bad: PASSWORD="secret123"
# Good: Read from secure sources

# Read from environment variables
DB_PASSWORD="${DB_PASSWORD:-}"

# Read from secure files
if [ -f "/run/secrets/db_password" ]; then
    DB_PASSWORD=$(cat /run/secrets/db_password)
fi

# Prompt user if not available
if [ -z "$DB_PASSWORD" ]; then
    echo -n "Enter database password: "
    read -s DB_PASSWORD
    echo
fi

# Use credentials securely (don't echo them)
# ... database operations ...

# Clear from memory
unset DB_PASSWORD
```

## 🧪 Testing Scripts

### Script Testing Framework
```bash
#!/bin/bash
# scripts/test-scripts.sh

# Test script functionality
test_setup_script() {
    echo "Testing setup-pre-commit.sh..."
    
    # Mock git repository
    git init test-repo
    cd test-repo
    
    # Copy script
    cp ../scripts/setup-pre-commit.sh .
    
    # Run script
    ./setup-pre-commit.sh
    
    # Verify pre-commit is installed
    if command -v pre-commit >/dev/null 2>&1; then
        echo "✅ Pre-commit installed successfully"
    else
        echo "❌ Pre-commit installation failed"
        return 1
    fi
    
    # Cleanup
    cd ..
    rm -rf test-repo
}

# Run tests
test_setup_script
```

### Automated Testing
```bash
#!/bin/bash
# scripts/run-all-tests.sh

echo "🧪 Running all automated tests..."

# Unit tests
echo "Running Python tests..."
python -m pytest

# Script tests
echo "Testing utility scripts..."
bash scripts/test-scripts.sh

# Integration tests
echo "Running integration tests..."
bash scripts/integration-test.sh

# Security tests
echo "Running security tests..."
python -m bandit -r .

echo "✅ All tests completed!"
```

## 🎓 Learning Path

**Beginner**: 
1. Learn basic bash scripting syntax
2. Understand file permissions and execution
3. Practice with simple automation tasks
4. Learn about environment variables and configuration

**Intermediate**: 
1. Study error handling and logging techniques
2. Learn about process management and signals
3. Practice with Docker and deployment scripts
4. Understand security best practices for scripts

**Advanced**: 
1. Create complex deployment pipelines
2. Implement script testing frameworks
3. Master performance optimization techniques
4. Build cross-platform compatibility

## 🔄 Development Workflow

### Creating New Scripts
1. **Plan the task** - Define what the script should accomplish
2. **Choose the approach** - Bash, Python, or other language
3. **Implement with error handling** - Use proper error checking
4. **Test thoroughly** - Test in different environments
5. **Document usage** - Add clear usage instructions
6. **Set permissions** - Make executable with `chmod +x`

### Script Maintenance
```bash
# Regular maintenance tasks
./scripts/update-dependencies.sh
./scripts/cleanup-logs.sh
./scripts/check-security.sh
./scripts/backup-data.sh
```

---

**Next**: Check out the main project [`README.md`](../README.md) for complete project overview and quick start guide!