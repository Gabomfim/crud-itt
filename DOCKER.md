# Guia de Deploy com Docker

## 🐳 Configuração Docker para API de Gerenciamento de Usuários

Este guia cobre a containerização e deploy da aplicação FastAPI usando Docker.

## Visão Geral dos Arquivos

- **`Dockerfile`** - Container principal da aplicação
- **`docker-compose.yml`** - Orquestração multi-serviço
- **`.dockerignore`** - Excluir arquivos do contexto de build
- **`nginx.conf`** - Configuração de proxy reverso

## Início Rápido

### 1. Build e Execução (Simples)
```bash
# Fazer build da imagem Docker
docker build -t user-management-api .

# Executar o container
docker run -p 8000:8000 user-management-api

# Acessar a aplicação em http://localhost:8000
```

### 2. Usando Docker Compose (Recomendado)
```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

## Serviços do Docker Compose

### 🚀 **Serviço da Aplicação (`app`)**
- Aplicação FastAPI
- Porta: 8000
- Health checks habilitados
- Volume montado para persistência do banco de dados

### 🐘 **Serviço PostgreSQL (`db`)**
- PostgreSQL 15 Alpine
- Porta: 5432
- Volume de dados persistente
- Health checks enabled

### 🌐 **Nginx Service (`nginx`)**
- Reverse proxy and load balancer
- Port: 80
- Security headers
- Gzip compression
- Rate limiting
- **Profile**: `production` (optional)

## Environment Configuration

### Development (SQLite)
```bash
# Uses SQLite database (default)
docker-compose up app
```

### Production (PostgreSQL)
```bash
# Edit docker-compose.yml to use PostgreSQL
# Update DATABASE_URL environment variable
DATABASE_URL=postgresql://postgres:password@db:5432/users_db

# Start with database
docker-compose up app db
```

### With Nginx (Production)
```bash
# Start all services including Nginx
docker-compose --profile production up -d
```

## Docker Features

### 🔒 **Security**
- Non-root user inside container
- Minimal base image (Python slim)
- Security headers via Nginx
- Environment variable configuration

### ⚡ **Performance**
- Multi-stage build optimization
- Docker layer caching
- Gzip compression
- Static file caching

### 🏥 **Health Monitoring**
- Application health checks
- Database connectivity checks
- Automatic restart policies

### 📊 **Observability**
- Structured logging
- Health check endpoints
- Container metrics ready

## Advanced Usage

### Custom Build Arguments
```bash
# Build with specific Python version
docker build --build-arg PYTHON_VERSION=3.11 -t user-api .
```

### Production Environment Variables
```bash
# Create .env file for production
cat > .env << EOF
DATABASE_URL=postgresql://user:pass@localhost:5432/proddb
SECRET_KEY=your-secret-key
DEBUG=false
EOF

# Run with environment file
docker-compose --env-file .env up -d
```

### Scaling Services
```bash
# Scale application instances
docker-compose up --scale app=3 -d

# View running containers
docker-compose ps
```

### Database Initialization
```bash
# Initialize database with sample data
docker-compose exec app python -m database.init
```

## Monitoring and Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail 100 app
```

### Container Stats
```bash
# Real-time stats
docker stats

# Container info
docker-compose exec app df -h
docker-compose exec app ps aux
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Use different port
docker run -p 8080:8000 user-management-api
```

#### Database Connection Issues
```bash
# Check database logs
docker-compose logs db

# Test database connectivity
docker-compose exec app ping db

# Reset database
docker-compose down -v
docker-compose up -d
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER ./database

# Recreate container
docker-compose down
docker-compose up --build -d
```

## Deployment Strategies

### 🚀 **Development**
```bash
docker-compose up
```

### 🏭 **Production**
```bash
# With PostgreSQL and Nginx
docker-compose --profile production up -d

# Or using external database
DATABASE_URL=postgresql://prod-db:5432/api docker-compose up -d
```

### ☁️ **Cloud Deployment**
- **AWS ECS/Fargate**: Use task definitions
- **Google Cloud Run**: Direct Docker image deployment
- **Kubernetes**: Use provided YAML configs
- **DigitalOcean App Platform**: Git-based deployment

## Resource Requirements

### Minimum
- **CPU**: 0.5 cores
- **Memory**: 512MB
- **Storage**: 1GB

### Recommended
- **CPU**: 1 core
- **Memory**: 1GB
- **Storage**: 5GB

Your FastAPI application is now fully containerized and production-ready! 🐳✨