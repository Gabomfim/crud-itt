#!/bin/bash

# Enhanced Deploy Script for GitHub Actions CI/CD
# Supports multiple environments and cloud providers
# Usage: ./deploy-enhanced.sh [environment] [image_tag] [namespace]

set -e

# Default values
ENVIRONMENT=${1:-development}
IMAGE_TAG=${2:-latest}
NAMESPACE=${3:-crud-itt}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(dirname "$SCRIPT_DIR")"
DEPLOYMENT_TIMEOUT=${DEPLOYMENT_TIMEOUT:-600}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    log_success "kubectl is available"
}

# Function to check if cluster is accessible
check_cluster() {
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        log_error "Please ensure your kubeconfig is properly configured"
        exit 1
    fi
    log_success "Kubernetes cluster is accessible"
}

# Function to create namespace if it doesn't exist
create_namespace() {
    local ns=$1
    if kubectl get namespace "$ns" &> /dev/null; then
        log_info "Namespace '$ns' already exists"
    else
        log_info "Creating namespace '$ns'"
        kubectl create namespace "$ns"
        log_success "Namespace '$ns' created"
    fi
}

# Function to apply environment-specific configurations
apply_environment_config() {
    local env=$1
    local ns=$2
    
    log_info "Applying $env environment configuration..."
    
    # Environment-specific settings
    case $env in
        "production")
            REPLICAS=3
            CPU_REQUEST="200m"
            CPU_LIMIT="1000m"
            MEMORY_REQUEST="256Mi"
            MEMORY_LIMIT="1Gi"
            LOG_LEVEL="WARNING"
            DEBUG_MODE="false"
            BCRYPT_ROUNDS="14"
            ;;
        "staging")
            REPLICAS=2
            CPU_REQUEST="100m"
            CPU_LIMIT="500m"
            MEMORY_REQUEST="128Mi"
            MEMORY_LIMIT="512Mi"
            LOG_LEVEL="INFO"
            DEBUG_MODE="false"
            BCRYPT_ROUNDS="12"
            ;;
        "development")
            REPLICAS=1
            CPU_REQUEST="50m"
            CPU_LIMIT="200m"
            MEMORY_REQUEST="64Mi"
            MEMORY_LIMIT="256Mi"
            LOG_LEVEL="DEBUG"
            DEBUG_MODE="true"
            BCRYPT_ROUNDS="10"
            ;;
        *)
            log_warning "Unknown environment '$env', using development defaults"
            REPLICAS=1
            CPU_REQUEST="50m"
            CPU_LIMIT="200m"
            MEMORY_REQUEST="64Mi"
            MEMORY_LIMIT="256Mi"
            LOG_LEVEL="DEBUG"
            DEBUG_MODE="true"
            BCRYPT_ROUNDS="10"
            ;;
    esac
    
    # Export for use in other functions
    export REPLICAS CPU_REQUEST CPU_LIMIT MEMORY_REQUEST MEMORY_LIMIT
    export LOG_LEVEL DEBUG_MODE BCRYPT_ROUNDS
    
    log_success "Environment configuration set for $env"
}

# Function to generate deployment manifest
generate_deployment_manifest() {
    local env=$1
    local ns=$2
    local image_tag=$3
    
    log_info "Generating deployment manifest for $env environment..."
    
    cat > "${K8S_DIR}/deployment-${env}.yaml" << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crud-itt-app
  namespace: $ns
  labels:
    app: fastapi-crud
    version: v1
    environment: $env
  annotations:
    deployment.kubernetes.io/revision: "1"
    kubernetes.io/change-cause: "Deployed via GitHub Actions - $(date)"
spec:
  replicas: $REPLICAS
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: fastapi-crud
  template:
    metadata:
      labels:
        app: fastapi-crud
        version: v1
        environment: $env
    spec:
      containers:
      - name: fastapi-crud
        image: ghcr.io/gabomfim/crud-itt:$image_tag
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
          protocol: TCP
        
        env:
        - name: APP_ENVIRONMENT
          value: "$env"
        - name: LOG_LEVEL
          value: "$LOG_LEVEL"
        - name: APP_DEBUG
          value: "$DEBUG_MODE"
        - name: SECURITY_BCRYPT_ROUNDS
          value: "$BCRYPT_ROUNDS"
        
        envFrom:
        - configMapRef:
            name: crud-itt-config
        - secretRef:
            name: crud-itt-secrets
        
        resources:
          requests:
            memory: "$MEMORY_REQUEST"
            cpu: "$CPU_REQUEST"
          limits:
            memory: "$MEMORY_LIMIT"
            cpu: "$CPU_LIMIT"
        
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL
EOF
    
    log_success "Deployment manifest generated: deployment-${env}.yaml"
}

# Function to apply Kubernetes manifests
apply_manifests() {
    local env=$1
    local ns=$2
    
    log_info "Applying Kubernetes manifests for $env environment..."
    
    # Apply base manifests with namespace substitution
    for file in "${K8S_DIR}"/*.yaml; do
        filename=$(basename "$file")
        
        # Skip environment-specific deployment files
        if [[ "$filename" == deployment-*.yaml ]]; then
            continue
        fi
        
        # Skip the base deployment.yaml as we use environment-specific one
        if [[ "$filename" == "deployment.yaml" ]]; then
            continue
        fi
        
        log_info "Applying $filename..."
        sed "s/namespace: crud-itt/namespace: $ns/g" "$file" | kubectl apply -f -
    done
    
    # Apply environment-specific deployment
    if [[ -f "${K8S_DIR}/deployment-${env}.yaml" ]]; then
        log_info "Applying environment-specific deployment..."
        kubectl apply -f "${K8S_DIR}/deployment-${env}.yaml"
    else
        log_error "Environment-specific deployment file not found: deployment-${env}.yaml"
        exit 1
    fi
    
    log_success "All manifests applied successfully"
}

# Function to wait for deployment
wait_for_deployment() {
    local ns=$1
    
    log_info "Waiting for deployment to be ready (timeout: ${DEPLOYMENT_TIMEOUT}s)..."
    
    if kubectl rollout status deployment/crud-itt-app \
        --namespace="$ns" \
        --timeout="${DEPLOYMENT_TIMEOUT}s"; then
        log_success "Deployment completed successfully"
    else
        log_error "Deployment failed or timed out"
        log_info "Getting pod status for debugging..."
        kubectl get pods -n "$ns" -l app=fastapi-crud
        kubectl describe pods -n "$ns" -l app=fastapi-crud
        exit 1
    fi
}

# Function to run health checks
run_health_checks() {
    local ns=$1
    
    log_info "Running health checks..."
    
    # Get service IP
    SERVICE_IP=$(kubectl get service crud-itt-service -n "$ns" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    if [[ -z "$SERVICE_IP" ]]; then
        SERVICE_IP=$(kubectl get service crud-itt-service -n "$ns" -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")
    fi
    
    if [[ -z "$SERVICE_IP" ]]; then
        log_warning "Could not determine service IP, skipping external health check"
        return 0
    fi
    
    log_info "Service IP: $SERVICE_IP"
    
    # Health check with retry
    local max_attempts=10
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        log_info "Health check attempt $attempt/$max_attempts..."
        
        if kubectl run health-check-${RANDOM} --rm -i --restart=Never --image=curlimages/curl:latest --timeout=30s -- \
            curl -f -m 10 "http://$SERVICE_IP:8000/health"; then
            log_success "Health check passed"
            return 0
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            log_error "Health check failed after $max_attempts attempts"
            return 1
        fi
        
        log_warning "Health check failed, retrying in 10 seconds..."
        sleep 10
        ((attempt++))
    done
}

# Function to show deployment summary
show_deployment_summary() {
    local env=$1
    local ns=$2
    local image_tag=$3
    
    echo
    echo "================== DEPLOYMENT SUMMARY =================="
    echo "Environment:       $env"
    echo "Namespace:         $ns"
    echo "Image Tag:         $image_tag"
    echo "Replicas:          $REPLICAS"
    echo "Resource Limits:   CPU=$CPU_LIMIT, Memory=$MEMORY_LIMIT"
    echo "Resource Requests: CPU=$CPU_REQUEST, Memory=$MEMORY_REQUEST"
    echo "Log Level:         $LOG_LEVEL"
    echo "Debug Mode:        $DEBUG_MODE"
    echo "Deployment Time:   $(date)"
    echo "========================================================"
    
    # Show pod status
    echo
    log_info "Current pod status:"
    kubectl get pods -n "$ns" -l app=fastapi-crud -o wide
    
    # Show service information
    echo
    log_info "Service information:"
    kubectl get services -n "$ns"
}

# Main deployment function
main() {
    log_info "🚀 Starting CRUD-ITT deployment..."
    log_info "Environment: $ENVIRONMENT"
    log_info "Image Tag: $IMAGE_TAG"
    log_info "Namespace: $NAMESPACE"
    
    # Pre-deployment checks
    check_kubectl
    check_cluster
    
    # Environment setup
    apply_environment_config "$ENVIRONMENT" "$NAMESPACE"
    create_namespace "$NAMESPACE"
    
    # Generate and apply manifests
    generate_deployment_manifest "$ENVIRONMENT" "$NAMESPACE" "$IMAGE_TAG"
    apply_manifests "$ENVIRONMENT" "$NAMESPACE"
    
    # Wait for deployment and run health checks
    wait_for_deployment "$NAMESPACE"
    
    if ! run_health_checks "$NAMESPACE"; then
        log_warning "Health check failed, but deployment is considered successful"
        log_info "Please verify the application manually"
    fi
    
    # Show summary
    show_deployment_summary "$ENVIRONMENT" "$NAMESPACE" "$IMAGE_TAG"
    
    log_success "🎉 Deployment completed successfully!"
}

# Handle script interruption
trap 'log_error "Deployment interrupted!"; exit 1' INT TERM

# Run main function
main "$@"