# Kubernetes Deployment Guide

This guide explains how to deploy the FastAPI CRUD application to Kubernetes.

## Prerequisites

- Kubernetes cluster (local or remote)
- `kubectl` configured to access your cluster
- Docker installed for building images
- For local development: Minikube, kind, or Docker Desktop with Kubernetes

## Quick Start

### 1. Deploy the Application

```bash
# Deploy to development environment (builds image locally)
./k8s/scripts/deploy.sh development

# Deploy to production environment (uses existing image)
./k8s/scripts/deploy.sh production
```

### 2. Monitor the Deployment

```bash
# Check deployment status
./k8s/scripts/monitor.sh status

# View application logs
./k8s/scripts/monitor.sh logs

# Follow logs in real-time
./k8s/scripts/monitor.sh logs -f
```

### 3. Access the Application

#### Local Development (Minikube/kind)
```bash
# Port forward to localhost
./k8s/scripts/monitor.sh port

# Or get the service URL (Minikube)
minikube service crud-itt-service -n crud-itt --url
```

#### Production
Configure your DNS to point `crud-itt.local` (or your chosen domain) to your ingress controller's IP address.

## Architecture

### Kubernetes Resources

The application deploys the following Kubernetes resources:

- **Namespace**: `crud-itt` - Isolated environment for the application
- **ConfigMap**: Application configuration (database URL, host, port, etc.)
- **Secret**: Sensitive data (JWT keys, passwords)
- **PersistentVolumeClaim**: Storage for SQLite database
- **Deployment**: Application pods with health checks and resource limits
- **Service**: Internal load balancer for the application
- **Ingress**: External access with NGINX ingress controller

### Resource Specifications

- **CPU**: 100m request, 500m limit per pod
- **Memory**: 128Mi request, 512Mi limit per pod
- **Replicas**: 2 (configurable in kustomization.yaml)
- **Storage**: 1Gi persistent volume for database

## Configuration

### Environment Variables

The application is configured through environment variables defined in the ConfigMap and Secret:

#### ConfigMap (`k8s/configmap.yaml`)
- `DATABASE_URL`: SQLite database connection string
- `HOST`: Application host (0.0.0.0)
- `PORT`: Application port (8000)
- `DEBUG`: Debug mode (false for production)
- `LOG_LEVEL`: Logging level (info)

#### Secret (`k8s/secret.yaml`)
- `JWT_SECRET_KEY`: Secret key for JWT authentication
- `DB_PASSWORD`: Database password (if using external DB)
- `ADMIN_USERNAME`: Admin username
- `ADMIN_PASSWORD`: Admin password

**Important**: Update the secrets with your own values before deploying to production!

### Customization

#### Scaling
To change the number of replicas:
```bash
kubectl scale deployment crud-itt-app --replicas=3 -n crud-itt
```

Or edit `k8s/kustomization.yaml`:
```yaml
replicas:
  - name: crud-itt-app
    count: 3
```

#### Resource Limits
Edit `k8s/deployment.yaml` to adjust CPU/memory limits:
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

#### Domain Configuration
Edit `k8s/ingress.yaml` to change the domain:
```yaml
spec:
  rules:
  - host: your-domain.com
```

## Management Scripts

### Deploy Script (`k8s/scripts/deploy.sh`)
- Builds Docker image (development mode)
- Applies all Kubernetes manifests
- Waits for deployment to be ready
- Shows deployment status and logs

### Monitor Script (`k8s/scripts/monitor.sh`)
- `status`: Show deployment status
- `logs`: Show application logs
- `pods`: Show pod information
- `events`: Show recent events
- `resources`: Show resource usage
- `port`: Port forward to localhost
- `shell`: Get shell access to a pod

### Cleanup Script (`k8s/scripts/cleanup.sh`)
- Removes all application resources
- Deletes the namespace
- Confirms before deletion

## Troubleshooting

### Common Issues

1. **Image Pull Errors**
   ```bash
   # For local development, ensure image is loaded
   docker build -t crud-itt:latest .
   minikube image load crud-itt:latest  # For Minikube
   kind load docker-image crud-itt:latest  # For kind
   ```

2. **Pod Not Starting**
   ```bash
   # Check pod events
   ./k8s/scripts/monitor.sh events
   
   # Check pod logs
   ./k8s/scripts/monitor.sh logs
   
   # Describe pod for detailed information
   kubectl describe pod -l app=fastapi-crud -n crud-itt
   ```

3. **Service Not Accessible**
   ```bash
   # Check service endpoints
   kubectl get endpoints crud-itt-service -n crud-itt
   
   # Test service internally
   kubectl run test-pod --image=busybox -n crud-itt --rm -it -- sh
   # Inside the pod: wget -O- http://crud-itt-service/
   ```

4. **Database Issues**
   ```bash
   # Check persistent volume
   kubectl get pv,pvc -n crud-itt
   
   # Check if database directory is mounted
   ./k8s/scripts/monitor.sh shell
   # Inside the pod: ls -la /app/data/
   ```

### Logs and Debugging

```bash
# View application logs
kubectl logs -l app=fastapi-crud -n crud-itt -f

# Get shell access to debug
kubectl exec -it deployment/crud-itt-app -n crud-itt -- /bin/bash

# Check resource usage
kubectl top pods -n crud-itt

# View events
kubectl get events -n crud-itt --sort-by='.lastTimestamp'
```

## Security Considerations

### Implemented Security Features

1. **Non-root container**: Runs as user 1000
2. **Read-only root filesystem**: Where possible
3. **Dropped capabilities**: All unnecessary capabilities removed
4. **Resource limits**: CPU and memory limits enforced
5. **Network policies**: Can be added for network segmentation
6. **Secret management**: Sensitive data stored in Kubernetes secrets

### Production Recommendations

1. **Use external database**: Replace SQLite with PostgreSQL or MySQL
2. **Enable TLS**: Configure HTTPS in ingress with proper certificates
3. **Add monitoring**: Integrate with Prometheus and Grafana
4. **Set up backups**: Regular database backups
5. **Use proper secrets**: Replace default secrets with strong, unique values
6. **Network policies**: Restrict network access between namespaces
7. **Resource quotas**: Set namespace resource quotas
8. **Pod security policies**: Enforce pod security standards

## Next Steps

1. **Monitoring**: Set up Prometheus and Grafana for monitoring
2. **Logging**: Configure centralized logging with ELK stack
3. **CI/CD**: Integrate with GitHub Actions for automated deployments
4. **Database**: Migrate to a production database like PostgreSQL
5. **Scaling**: Configure Horizontal Pod Autoscaler (HPA)
6. **Security**: Implement network policies and pod security policies

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Kubernetes logs and events
3. Consult the application documentation
4. Check the GitHub repository for updates