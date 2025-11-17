#!/bin/bash

# Cleanup CRUD-ITT Application from Kubernetes
# Usage: ./cleanup.sh

set -e

NAMESPACE="crud-itt"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(dirname "$SCRIPT_DIR")"

echo "🧹 Cleaning up CRUD-ITT Application from Kubernetes..."

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        echo "❌ kubectl is not installed or not in PATH"
        exit 1
    fi
}

# Function to delete resources
cleanup_resources() {
    echo "🗑️  Deleting Kubernetes resources..."
    
    # Delete using kustomize (this will delete all resources defined in kustomization.yaml)
    kubectl delete -k "$K8S_DIR" --ignore-not-found=true
    
    # Wait a bit for resources to be deleted
    echo "⏳ Waiting for resources to be deleted..."
    sleep 5
    
    # Check if namespace still exists and delete it if it does
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        echo "🗑️  Deleting namespace $NAMESPACE..."
        kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
    fi
}

# Function to show remaining resources (if any)
show_status() {
    echo "📊 Checking for remaining resources..."
    
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        echo "⚠️  Some resources might still be terminating:"
        kubectl get all -n "$NAMESPACE" 2>/dev/null || echo "No resources found in namespace $NAMESPACE"
    else
        echo "✅ All resources have been deleted successfully"
    fi
}

# Main execution
main() {
    check_kubectl
    
    # Confirm deletion
    read -p "Are you sure you want to delete all CRUD-ITT resources? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cleanup cancelled"
        exit 1
    fi
    
    cleanup_resources
    show_status
    
    echo "🎉 Cleanup completed!"
}

# Run main function
main "$@"