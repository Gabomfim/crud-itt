# Kubernetes Directory ☸️

This directory contains all Kubernetes configuration files for deploying the CRUD ITT application to a Kubernetes cluster.

## 🎯 Purpose

The `k8s/` directory provides production-ready Kubernetes deployment configurations that allow you to run the application at scale with high availability, automatic scaling, and proper monitoring.

## 📁 Directory Structure

```
k8s/
├── configmap.yaml       # Application configuration
├── deployment.yaml      # Application deployment
├── ingress.yaml         # External access configuration
├── kustomization.yaml   # Kustomize configuration management
├── namespace.yaml       # Kubernetes namespace
├── pvc.yaml            # Persistent storage
├── secret.yaml         # Sensitive data (passwords, tokens)
├── service.yaml        # Internal networking
└── scripts/            # Deployment automation scripts
    ├── cleanup.sh      # Clean up resources
    ├── deploy.sh       # Basic deployment
    ├── deploy-enhanced.sh  # Advanced deployment with checks
    └── monitor.sh      # Monitoring and status checks
```

## 📄 File Overview

### `namespace.yaml` - Environment Isolation
**Purpose**: Creates isolated environment for the application

**What it does**:
- Creates separate namespace (e.g., `crud-itt`, `crud-itt-staging`)
- Isolates resources from other applications
- Provides security boundaries
- Enables resource quotas and limits

**For beginners**: Think of a namespace as a "separate apartment" in the Kubernetes building - your app lives there without interfering with other apps.

### `configmap.yaml` - Configuration Management
**Purpose**: Stores non-sensitive configuration data

**What it does**:
- Stores environment variables
- Application settings (log levels, features)
- Database connection strings (non-sensitive parts)
- CORS settings and other configuration

**For beginners**: This is like a "settings file" that tells your app how to behave in the Kubernetes environment.

### `secret.yaml` - Sensitive Data Storage
**Purpose**: Securely stores passwords, tokens, and other secrets

**What it does**:
- JWT secret keys
- Database passwords
- API keys
- SSL certificates

**For beginners**: This is like a "password manager" for your application - it keeps all the secret information safe and encrypted.

### `deployment.yaml` - Application Deployment
**Purpose**: Defines how the application should run

**What it does**:
- Specifies number of app instances (replicas)
- Defines resource limits (CPU, memory)
- Sets up health checks
- Configures rolling updates
- Manages container lifecycle

**For beginners**: This is the "instruction manual" that tells Kubernetes how many copies of your app to run and how to manage them.

### `service.yaml` - Internal Networking
**Purpose**: Provides stable network access to the application

**What it does**:
- Creates internal DNS name for the app
- Load balances traffic between app instances
- Exposes ports for communication
- Enables service discovery

**For beginners**: This is like the "internal phone system" that lets other parts of Kubernetes talk to your app.

### `ingress.yaml` - External Access
**Purpose**: Configures external access from the internet

**What it does**:
- Maps domain names to the application
- Handles SSL/TLS termination
- Manages routing rules
- Provides load balancing

**For beginners**: This is like the "front door" of your application that handles visitors from the internet.

### `pvc.yaml` - Persistent Storage
**Purpose**: Provides persistent storage for the database

**What it does**:
- Creates storage volumes
- Ensures data survives pod restarts
- Manages backup and recovery
- Handles storage expansion

**For beginners**: This is like a "hard drive" that keeps your data safe even if the application restarts.

## 🚀 Deployment Process

### Quick Deployment
```bash
# Deploy everything at once
kubectl apply -k k8s/

# Check deployment status
kubectl get pods -n crud-itt
```

### Step-by-Step Deployment
```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Create secrets (set your actual secrets first!)
kubectl apply -f k8s/secret.yaml

# 3. Create configuration
kubectl apply -f k8s/configmap.yaml

# 4. Create storage
kubectl apply -f k8s/pvc.yaml

# 5. Deploy application
kubectl apply -f k8s/deployment.yaml

# 6. Create service
kubectl apply -f k8s/service.yaml

# 7. Set up external access
kubectl apply -f k8s/ingress.yaml
```

### Using Deployment Scripts
```bash
# Enhanced deployment with monitoring
./k8s/scripts/deploy-enhanced.sh

# Monitor deployment progress
./k8s/scripts/monitor.sh

# Clean up everything
./k8s/scripts/cleanup.sh
```

## ⚙️ Configuration Examples

### Environment-Specific Deployments

**Development Environment**:
```yaml
# Lower resource limits
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"

# Single replica
replicas: 1

# Debug logging
env:
  - name: LOG_LEVEL
    value: "DEBUG"
```

**Production Environment**:
```yaml
# Higher resource limits
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"

# Multiple replicas for high availability
replicas: 3

# Production logging
env:
  - name: LOG_LEVEL
    value: "INFO"
```

### Scaling Configuration
```yaml
# deployment.yaml
spec:
  replicas: 3  # Run 3 copies of the app
  
  # Horizontal Pod Autoscaler
  ---
  apiVersion: autoscaling/v2
  kind: HorizontalPodAutoscaler
  metadata:
    name: crud-itt-hpa
  spec:
    scaleTargetRef:
      apiVersion: apps/v1
      kind: Deployment
      name: crud-itt
    minReplicas: 2
    maxReplicas: 10
    metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

## 🛡️ Security Configuration

### Pod Security Standards
```yaml
# deployment.yaml
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: crud-itt
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
```

### Network Policies
```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: crud-itt-network-policy
spec:
  podSelector:
    matchLabels:
      app: crud-itt
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-system
    ports:
    - protocol: TCP
      port: 8000
```

### Secret Management
```yaml
# secret.yaml (example - use actual secrets!)
apiVersion: v1
kind: Secret
metadata:
  name: crud-itt-secrets
type: Opaque
stringData:
  JWT_SECRET_KEY: "your-super-secret-jwt-key-32-chars-minimum"
  SECURITY_SECRET_KEY: "your-app-secret-key-32-chars-minimum"
  DATABASE_PASSWORD: "your-secure-database-password"
```

## 📊 Monitoring and Health Checks

### Liveness Probe
```yaml
# Checks if app is running
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### Readiness Probe
```yaml
# Checks if app is ready to receive traffic
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

### Startup Probe
```yaml
# Gives app time to start up
startupProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 30
```

## 🔄 Rolling Updates

### Update Strategy
```yaml
# deployment.yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1      # Keep most instances running
      maxSurge: 1           # Add one extra during update
```

### Deployment Commands
```bash
# Update image version
kubectl set image deployment/crud-itt crud-itt=crud-itt:v2.0.0 -n crud-itt

# Monitor rollout
kubectl rollout status deployment/crud-itt -n crud-itt

# Rollback if needed
kubectl rollout undo deployment/crud-itt -n crud-itt
```

## 💾 Database Integration

### SQLite (Development)
```yaml
# Use persistent volume for SQLite file
volumeMounts:
- name: database-storage
  mountPath: /app/database
volumes:
- name: database-storage
  persistentVolumeClaim:
    claimName: crud-itt-pvc
```

### PostgreSQL (Production)
```yaml
# Connect to external PostgreSQL
env:
- name: DATABASE_URL
  value: "postgresql+asyncpg://user:password@postgresql-service:5432/crud_itt"
```

## 🌐 Ingress Configuration

### Basic HTTP Ingress
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: crud-itt-ingress
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: crud-itt-service
            port:
              number: 8000
```

### HTTPS with SSL
```yaml
# ingress.yaml with TLS
spec:
  tls:
  - hosts:
    - api.example.com
    secretName: crud-itt-tls
  rules:
  - host: api.example.com
    # ... rest of configuration
```

## 🔧 Troubleshooting

### Common Issues

**Pods Not Starting**:
```bash
# Check pod status
kubectl get pods -n crud-itt

# Check pod logs
kubectl logs -f deployment/crud-itt -n crud-itt

# Describe pod for events
kubectl describe pod <pod-name> -n crud-itt
```

**Service Not Accessible**:
```bash
# Check service
kubectl get service -n crud-itt

# Test service connectivity
kubectl port-forward service/crud-itt-service 8000:8000 -n crud-itt
```

**Configuration Issues**:
```bash
# Check configmap
kubectl get configmap crud-itt-config -n crud-itt -o yaml

# Check secrets
kubectl get secret crud-itt-secrets -n crud-itt -o yaml
```

### Debugging Commands
```bash
# Get all resources
kubectl get all -n crud-itt

# Check events
kubectl get events -n crud-itt --sort-by='.lastTimestamp'

# Shell into running pod
kubectl exec -it deployment/crud-itt -n crud-itt -- /bin/bash

# View resource usage
kubectl top pods -n crud-itt
```

## 🎓 Learning Path

**Beginner**: 
1. Understand what each YAML file does
2. Try deploying to a local Kubernetes cluster (minikube)
3. Learn basic kubectl commands
4. Experiment with scaling replicas

**Intermediate**: 
1. Study resource limits and requests
2. Learn about health checks and probes
3. Practice with rolling updates
4. Set up monitoring and logging

**Advanced**: 
1. Implement custom operators
2. Set up GitOps workflows
3. Design multi-environment deployments
4. Optimize for cost and performance

## 🏗️ Infrastructure Requirements

### Minimum Cluster Requirements
- **Kubernetes Version**: 1.20+
- **Nodes**: 2+ worker nodes
- **CPU**: 2+ cores total
- **Memory**: 4GB+ total
- **Storage**: 20GB+ persistent storage

### Recommended Production Setup
- **Nodes**: 3+ worker nodes
- **CPU**: 8+ cores total
- **Memory**: 16GB+ total
- **Storage**: 100GB+ SSD storage
- **Load Balancer**: External load balancer
- **Monitoring**: Prometheus + Grafana

---

**Next**: Check out the [`static/`](../static/README.md) and [`templates/`](../templates/README.md) directories for web interface files!