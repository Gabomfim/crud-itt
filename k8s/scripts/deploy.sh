#!/bin/bash

# Deploy CRUD-ITT Application to Kubernetes
# Usage: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-development}
NAMESPACE="crud-itt"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Deploying CRUD-ITT Application to Kubernetes..."
echo "Environment: $ENVIRONMENT"
echo "Namespace: $NAMESPACE"

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        echo "❌ kubectl is not installed or not in PATH"
        exit 1
    fi
    echo "✅ kubectl is available"
}

# Function to check if cluster is accessible
check_cluster() {
    if ! kubectl cluster-info &> /dev/null; then
        echo "❌ Cannot connect to Kubernetes cluster"
        echo "Please ensure your kubeconfig is properly configured"
        exit 1
    fi
    echo "✅ Kubernetes cluster is accessible"
}

# Function to build and load Docker image (for local development)
build_image() {
    echo "🔨 Building Docker image..."
    cd "$K8S_DIR/.."
    
    # Build the image
    docker build -t crud-itt:latest .
    
    # For local clusters (minikube, kind, etc.), load the image
    if kubectl config current-context | grep -E "(minikube|kind)" &> /dev/null; then
        echo "📦 Loading image into local cluster..."
        if command -v minikube &> /dev/null; then
            minikube image load crud-itt:latest
        elif command -v kind &> /dev/null; then
            kind load docker-image crud-itt:latest
        fi
    fi
    
    cd "$K8S_DIR"
}

# Function to apply Kubernetes manifests
apply_manifests() {
    echo "📋 Applying Kubernetes manifests..."
    
    # Apply using kustomize
    kubectl apply -k "$K8S_DIR"
    
    echo "⏳ Waiting for deployment to be ready..."
    kubectl rollout status deployment/crud-itt-app -n "$NAMESPACE" --timeout=300s
}

# Function to show deployment status
show_status() {
    echo "📊 Deployment Status:"
    echo "===================="
    
    kubectl get all -n "$NAMESPACE"
    
    echo ""
    echo "🔗 Service Information:"
    kubectl get svc crud-itt-service -n "$NAMESPACE"
    
    echo ""
    echo "🌐 Ingress Information:"
    kubectl get ingress crud-itt-ingress -n "$NAMESPACE"
    
    # Get service URL
    if kubectl config current-context | grep -E "(minikube)" &> /dev/null; then
        echo ""
        echo "🌍 Access URL (Minikube):"
        minikube service crud-itt-service -n "$NAMESPACE" --url
    fi
}

# Function to show logs
show_logs() {
    echo ""
    echo "📝 Recent logs:"
    kubectl logs -l app=fastapi-crud -n "$NAMESPACE" --tail=10
}

# Main execution
main() {
    check_kubectl
    check_cluster
    
    if [[ "$ENVIRONMENT" == "development" ]]; then
        build_image
    fi
    
    apply_manifests
    show_status
    show_logs
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo ""
    echo "To access the application:"
    echo "- Local cluster: Use 'minikube service crud-itt-service -n crud-itt' or port-forward"
    echo "- Remote cluster: Configure your ingress domain and access via HTTPS"
    echo ""
    echo "Useful commands:"
    echo "- Check status: kubectl get all -n $NAMESPACE"
    echo "- View logs: kubectl logs -l app=fastapi-crud -n $NAMESPACE -f"
    echo "- Port forward: kubectl port-forward svc/crud-itt-service 8000:80 -n $NAMESPACE"
}

# Run main function
main "$@"