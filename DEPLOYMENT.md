# GitHub Actions Deployment Setup

This document provides instructions for setting up the GitHub Actions deployment workflows for staging and production environments.

## Overview

The deployment system includes:
- **Staging Deployment**: Triggered on pushes to `staging` branch
- **Production Deployment**: Triggered on pushes to `main` branch
- **Enhanced Security**: Includes vulnerability scanning, staging verification, and rollback capabilities
- **Multi-Environment Support**: Configurable for different cloud providers and Kubernetes clusters

## Required Secrets

### Repository Secrets

Configure these secrets in your GitHub repository settings (`Settings > Secrets and variables > Actions`):

#### Container Registry
```
GITHUB_TOKEN (automatically provided by GitHub)
```

#### Kubernetes Configuration
```
# For staging environment
KUBE_CONFIG_STAGING: Base64 encoded kubeconfig for staging cluster

# For production environment  
KUBE_CONFIG_PRODUCTION: Base64 encoded kubeconfig for production cluster
```

#### AWS (if using EKS)
```
AWS_ACCESS_KEY_ID: AWS access key ID
AWS_SECRET_ACCESS_KEY: AWS secret access key
AWS_REGION: AWS region (e.g., us-west-2)
EKS_CLUSTER_NAME: Name of your EKS cluster
CLOUD_PROVIDER: aws
```

#### Database Configuration
```
# Staging
STAGING_DATABASE_URL: Database connection string for staging
STAGING_DB_PASSWORD: Database password for staging

# Production
PRODUCTION_DATABASE_URL: Database connection string for production
PRODUCTION_DB_PASSWORD: Database password for production
```

#### Application Secrets
```
# Staging
STAGING_SECRET_KEY: Secret key for staging (min 32 characters)
STAGING_URL: URL of staging environment (for health checks)

# Production
PRODUCTION_SECRET_KEY: Secret key for production (min 32 characters)
PRODUCTION_URL: URL of production environment
```

#### Notifications (Optional)
```
SLACK_WEBHOOK_URL: Slack webhook URL for deployment notifications
NOTIFICATION_EMAIL: Email for critical production failure notifications

# SMTP settings for email notifications
SMTP_SERVER: SMTP server address
SMTP_PORT: SMTP server port
SMTP_USERNAME: SMTP username
SMTP_PASSWORD: SMTP password
```

## Environment Configuration

### GitHub Environments

Create the following environments in your repository (`Settings > Environments`):

#### Staging Environment
- **Name**: `staging`
- **Protection rules**: None (automatic deployment)
- **Environment secrets**: Same as repository secrets with `STAGING_` prefix

#### Production Environment
- **Name**: `production`
- **Protection rules**: 
  - Required reviewers (recommended)
  - Wait timer (optional, e.g., 5 minutes)
  - Restrict pushes to protected branches
- **Environment secrets**: Same as repository secrets with `PRODUCTION_` prefix

### Kubernetes Setup

#### 1. Create Kubeconfig Files

For each environment, create a kubeconfig file and encode it:

```bash
# Get your kubeconfig
kubectl config view --raw > staging-kubeconfig.yaml

# Encode to base64
cat staging-kubeconfig.yaml | base64 -w 0 > staging-kubeconfig-b64.txt

# Use the content of staging-kubeconfig-b64.txt as KUBE_CONFIG_STAGING secret
```

#### 2. Create Required Kubernetes Resources

**Namespace:**
```bash
kubectl create namespace crud-itt
kubectl create namespace crud-itt-staging
```

**Service Account (if using RBAC):**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: github-actions
  namespace: crud-itt
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: github-actions
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: github-actions
  namespace: crud-itt
```

## Deployment Workflow Features

### Staging Deployment (`deploy-staging.yml`)

**Triggers:**
- Push to `staging` branch
- Manual workflow dispatch

**Features:**
- Runs tests before deployment
- Builds and pushes Docker image
- Deploys to staging namespace
- Health checks
- Slack notifications

**Manual Trigger Options:**
- `force_deploy`: Skip tests and deploy anyway

### Production Deployment (`deploy-production.yml`)

**Triggers:**
- Push to `main` branch
- Manual workflow dispatch

**Features:**
- Comprehensive testing
- Security vulnerability scanning
- Staging environment verification
- Blue-green deployment strategy
- Automatic rollback on failure
- Health checks and smoke tests
- Stakeholder notifications

**Manual Trigger Options:**
- `force_deploy`: Skip tests and deploy anyway
- `skip_staging_check`: Skip staging verification

## Database Configuration Examples

### PostgreSQL
```
# Staging
STAGING_DATABASE_URL=postgresql+asyncpg://user:password@staging-db:5432/crud_itt

# Production  
PRODUCTION_DATABASE_URL=postgresql+asyncpg://user:password@prod-db:5432/crud_itt
```

### MySQL
```
# Staging
STAGING_DATABASE_URL=mysql+aiomysql://user:password@staging-db:3306/crud_itt

# Production
PRODUCTION_DATABASE_URL=mysql+aiomysql://user:password@prod-db:3306/crud_itt
```

### SQLite (not recommended for production)
```
STAGING_DATABASE_URL=sqlite+aiosqlite:///./database/staging.db
```

## Security Best Practices

1. **Secret Management**:
   - Use strong, unique secret keys (32+ characters)
   - Rotate secrets regularly
   - Never commit secrets to code

2. **Database Security**:
   - Use connection pooling
   - Enable SSL/TLS connections
   - Restrict database access by IP

3. **Kubernetes Security**:
   - Use namespaces for isolation
   - Implement RBAC
   - Use service accounts with minimal permissions
   - Enable network policies

4. **Container Security**:
   - Scan images for vulnerabilities
   - Use non-root users
   - Minimize container privileges

## Monitoring and Observability

### Health Checks
The deployments include multiple health check layers:
- Kubernetes liveness probes
- Kubernetes readiness probes
- Application health endpoints
- Post-deployment smoke tests

### Logging
Configure log levels per environment:
- Development: `DEBUG`
- Staging: `INFO`
- Production: `WARNING`

### Metrics Integration
Add environment variables for monitoring tools:
```
DATADOG_API_KEY: Your Datadog API key
NEW_RELIC_LICENSE_KEY: Your New Relic license key
```

## Troubleshooting

### Common Issues

1. **Deployment Timeout**:
   - Check resource limits
   - Verify image availability
   - Check cluster capacity

2. **Health Check Failures**:
   - Verify service configuration
   - Check application startup time
   - Review application logs

3. **Database Connection Issues**:
   - Verify connection strings
   - Check network policies
   - Confirm database availability

### Debugging Commands

```bash
# Check pod status
kubectl get pods -n crud-itt -l app=fastapi-crud

# View pod logs
kubectl logs -f deployment/crud-itt-app -n crud-itt

# Check recent events
kubectl get events -n crud-itt --sort-by='.firstTimestamp'

# Describe failing pods
kubectl describe pods -n crud-itt -l app=fastapi-crud
```

## Rollback Procedures

### Automatic Rollback
Production deployments include automatic rollback on:
- Health check failures
- Deployment timeout
- Application startup failures

### Manual Rollback
```bash
# View rollout history
kubectl rollout history deployment/crud-itt-app -n crud-itt

# Rollback to previous version
kubectl rollout undo deployment/crud-itt-app -n crud-itt

# Rollback to specific revision
kubectl rollout undo deployment/crud-itt-app --to-revision=2 -n crud-itt
```

## Branch Strategy

### Recommended Git Flow
```
feature/branch → staging → main
                    ↓        ↓
               staging-env  production-env
```

1. Develop features in feature branches
2. Merge to `staging` for staging deployment
3. Test in staging environment
4. Merge to `main` for production deployment

### Branch Protection Rules
Configure these in GitHub repository settings:
- Require pull request reviews
- Require status checks to pass
- Require branches to be up to date
- Restrict pushes to matching branches

## Next Steps

1. Set up all required secrets in GitHub repository
2. Create Kubernetes environments and namespaces
3. Configure database connections
4. Test staging deployment first
5. Configure monitoring and alerting
6. Set up branch protection rules
7. Train team on deployment procedures

For questions or issues, refer to the repository documentation or contact the DevOps team.