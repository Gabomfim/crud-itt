# crud-itt

[![CI/CD Pipeline](https://github.com/Gabomfim/crud-itt/actions/workflows/ci.yml/badge.svg)](https://github.com/Gabomfim/crud-itt/actions/workflows/ci.yml)
[![Deploy to Staging](https://github.com/Gabomfim/crud-itt/actions/workflows/deploy-staging.yml/badge.svg)](https://github.com/Gabomfim/crud-itt/actions/workflows/deploy-staging.yml)
[![Deploy to Production](https://github.com/Gabomfim/crud-itt/actions/workflows/deploy-production.yml/badge.svg)](https://github.com/Gabomfim/crud-itt/actions/workflows/deploy-production.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# CRUD ITT - API de Gerenciamento de Usuários

Uma aplicação FastAPI abrangente com funcionalidades completas de gerenciamento de usuários, autenticação e recursos de segurança.

## 🚀 Visão Geral do Projeto

Esta é uma API REST pronta para produção construída com FastAPI que fornece funcionalidade completa de gerenciamento de usuários incluindo:

- **Registro e Autenticação de Usuários** - Contas de usuário seguras com tokens JWT
- **Gerenciamento de Senhas** - Hash seguro de senhas e funcionalidade de alteração
- **Operações CRUD de Usuários** - Criar, Ler, Atualizar, Deletar usuários
- **Recursos de Segurança** - Autenticação JWT, validação de senha, limitação de taxa
- **Integração com Banco de Dados** - SQLAlchemy assíncrono com suporte a múltiplos bancos de dados
- **Pronto para Produção** - Logging, monitoramento, suporte Docker, deploy Kubernetes

## 📁 Estrutura do Projeto

```
crud-itt/
├── api/                    # Endpoints da API e rotas
├── config/                 # Configuração da aplicação
├── database/               # Conexões e modelos do banco de dados
├── models/                 # Modelos de dados e validação
├── services/               # Camada de lógica de negócio
├── utils/                  # Funções utilitárias e middleware
├── static/                 # Arquivos estáticos (CSS, imagens)
├── templates/              # Templates HTML
├── tests/                  # Suíte de testes
├── k8s/                    # Arquivos de deploy Kubernetes
├── scripts/                # Scripts utilitários
├── backup/                 # Configurações de backup
├── app.py                  # Ponto de entrada principal da aplicação
└── requirements files      # Dependências Python
```

## 🏁 Início Rápido

### Pré-requisitos
- Python 3.11+
- PostgreSQL ou SQLite (para banco de dados)
- Docker (opcional, para deploy containerizado)

### Instalação

1. **Clone o repositório**
   ```bash
   git clone <repository-url>
   cd crud-itt
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Edite o .env com sua configuração
   ```

4. **Inicialize o banco de dados**
   ```bash
   python -m database.init
   ```

5. **Execute a aplicação**
   ```bash
   python app.py
   ```

A API estará disponível em `http://localhost:8000`

## 📚 Documentação da API

Uma vez executando, visite:
- **Documentação Interativa da API**: http://localhost:8000/docs
- **Documentação Alternativa**: http://localhost:8000/redoc

## 🔑 Autenticação

A API usa JWT (JSON Web Tokens) para autenticação:

1. **Registre** um novo usuário: `POST /api/v1/users`
2. **Faça login** para obter token: `POST /api/v1/auth/login`  
3. **Use o token** nos cabeçalhos: `Authorization: Bearer <seu-token>`

## 🗂️ Guia de Diretórios

Cada diretório contém um README detalhado explicando seu propósito:

- [`api/`](api/README.md) - Endpoints da API e roteamento
- [`config/`](config/README.md) - Gerenciamento de configuração
- [`database/`](database/README.md) - Conexões do banco de dados e ORM
- [`models/`](models/README.md) - Modelos de validação de dados
- [`services/`](services/README.md) - Camada de lógica de negócio
- [`utils/`](utils/README.md) - Utilitários e middleware
- [`tests/`](tests/README.md) - Suíte de testes
- [`k8s/`](k8s/README.md) - Deploy Kubernetes
- [`static/`](static/README.md) - Assets web estáticos
- [`templates/`](templates/README.md) - Templates HTML
- [`scripts/`](scripts/README.md) - Scripts utilitários

## 🛠️ Principais Recursos

### Segurança
- ✅ Autenticação com token JWT
- ✅ Hash de senha com Bcrypt
- ✅ Validação e sanitização de entrada
- ✅ Prevenção de injeção SQL
- ✅ Configuração CORS
- ✅ Limitação de taxa pronta

### Performance
- ✅ Async/await em toda parte
- ✅ Pool de conexões do banco de dados
- ✅ Padrões de consulta eficientes
- ✅ Cache de requisição/resposta
- ✅ Logging estruturado

### Desenvolvimento
- ✅ Suíte de testes abrangente
- ✅ Containerização Docker
- ✅ Deploy Kubernetes
- ✅ Configuração baseada em ambiente
- ✅ Documentação do código
- ✅ Type hints em toda parte

## 🧪 Testes

Execute a suíte de testes:
```bash
# Execute todos os testes
python -m pytest

# Execute com cobertura
python -m pytest --cov=.

# Execute arquivo de teste específico
python -m pytest tests/test_auth.py
```

## 🐳 Deploy Docker

Construa e execute com Docker:
```bash
# Construir imagem
docker build -t crud-itt .

# Executar container
docker run -p 8000:8000 crud-itt

# Ou use docker-compose
docker-compose up
```

## ☸️ Deploy Kubernetes

Deploy no Kubernetes:
```bash
# Aplicar todas as configurações
kubectl apply -k k8s/

# Verificar status do deployment
kubectl get pods -n crud-itt
```

## 📝 Configuração de Ambiente

Principais variáveis de ambiente:

```bash
# Aplicação
APP_NAME=CRUD ITT
APP_ENVIRONMENT=development
APP_DEBUG=false

# Banco de Dados
DATABASE_URL=sqlite+aiosqlite:///./database/users.db

# Segurança
JWT_SECRET_KEY=sua-chave-secreta-aqui
SECURITY_SECRET_KEY=seu-app-secret-aqui

# Servidor
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

## 🚀 Workflows de Deploy

Este projeto inclui workflows automatizados de deploy para ambientes de staging e produção:

### Deploy de Staging
- **Trigger**: Push para branch `staging`
- **Ambiente**: namespace `crud-itt-staging`
- **Recursos**: 
  - Testes automatizados
  - Build e push da imagem Docker
  - Deploy Kubernetes
  - Verificações de saúde
  - Notificações Slack

### Deploy de Produção  
- **Trigger**: Push para branch `main`
- **Ambiente**: namespace `crud-itt`
- **Recursos**:
  - Testes abrangentes e escaneamento de segurança
  - Verificação do ambiente de staging
  - Deploy blue-green
  - Rollback automático em caso de falha
  - Verificações de saúde e smoke tests
  - Notificações multi-nível

### Deploy Manual
Ambos workflows suportam trigger manual com opções adicionais:
- `force_deploy`: Pular testes e fazer deploy mesmo assim
- `skip_staging_check`: (Somente produção) Pular verificação de staging

## 📋 Requisitos de Deploy

Antes de usar os workflows de deploy, certifique-se que você tem:

1. **GitHub Secrets configurados** (veja [DEPLOYMENT.md](DEPLOYMENT.md))
2. **Clusters Kubernetes** configurados para staging e produção
3. **Acesso ao registry de containers** (GitHub Container Registry)
4. **Instâncias de banco de dados** configuradas para cada ambiente

Para instruções detalhadas de configuração, veja o [Guia de Deploy](DEPLOYMENT.md).

## 🔧 Configuração de Ambiente

A aplicação usa configurações Pydantic para gerenciamento type-safe de variáveis de ambiente:

```python
from config import settings

# Configurações da aplicação
print(f"App: {settings.app.name} v{settings.app.version}")
print(f"Ambiente: {settings.app.environment}")

# Configurações do banco de dados  
print(f"URL do Banco de Dados: {settings.database.url}")

# Configurações de segurança
print(f"Rounds BCrypt: {settings.security.bcrypt_rounds}")
```

Veja `config/settings.py` para todas as opções de configuração disponíveis.

## 📊 Monitoramento de Saúde

A aplicação inclui monitoramento de saúde integrado:

- **Endpoint de Saúde**: `GET /health`
- **Probes Kubernetes**: Verificações de liveness e readiness
- **Logging**: Logging estruturado com níveis configuráveis
- **Métricas**: Pronto para integração com ferramentas de monitoramento

## 🔐 Recursos de Segurança

- **Segurança de Senha**: Requisitos de complexidade configuráveis
- **Hash BCrypt**: Contagens de rounds específicas por ambiente
- **Gerenciamento de Secrets**: Integração com secrets Kubernetes
- **Segurança de Container**: Usuário não-root, privilégios mínimos
- **Escaneamento de Vulnerabilidades**: Scans automatizados Trivy no CI/CD

## 📚 Endpoints da API

### Autenticação

- **POST** `/api/v1/auth/login` - Login e receber token JWT
- **POST** `/api/v1/auth/logout` - Logout e colocar token na blacklist  
- **GET** `/api/v1/auth/me` - Obter informações do usuário atual

#### Requisição de Login
```json
{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

#### Resposta de Login
```json
{
  "user": {
    "id": 1,
    "username": "seu_usuario",
    "age": 25,
    "description": "Descrição do usuário"
  },
  "token": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "message": "Login realizado com sucesso"
}
```

### Gerenciamento de Usuários (🔒 Autenticação Obrigatória)

- **GET** `/api/v1/users/{username}` - Obter informações do usuário
- **GET** `/api/v1/users?minimum_age={age}` - Obter usuários por idade mínima
- **POST** `/api/v1/users` - Criar um novo usuário (⚠️ Endpoint público)
- **PUT** `/api/v1/users/{username}` - Atualizar informações do usuário
- **DELETE** `/api/v1/users/{username}` - Deletar um usuário

### Gerenciamento de Senhas (🔒 Autenticação Obrigatória)

- **PUT** `/api/v1/users/{username}/password` - Alterar senha do usuário

#### Requisição de Alteração de Senha
```json
{
  "current_password": "senha_atual",
  "new_password": "nova_senha_segura",
  "confirm_password": "nova_senha_segura"
}
```

**Requisitos:**
- Senha atual deve estar correta
- Nova senha deve atender aos requisitos de complexidade (configurável)
- Nova senha deve ser diferente da senha atual
- Confirmação de senha deve coincidir com a nova senha

**Resposta:**
```json
{
  "message": "Senha alterada com sucesso"
}
```

### Cabeçalhos de Autenticação

Para endpoints protegidos, inclua o token JWT no cabeçalho Authorization:

```bash
Authorization: Bearer seu_jwt_token_aqui
```

### Exemplo de Uso

```bash
# 1. Login para obter token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "TestPassword123!"}'

# 2. Use token para endpoints protegidos
curl -X GET "http://localhost:8000/api/v1/users/testuser" \
  -H "Authorization: Bearer seu_jwt_token_aqui"

# 3. Logout para colocar token na blacklist
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer seu_jwt_token_aqui"
```
