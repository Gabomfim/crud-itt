#!/bin/bash

# Monitor CRUD-ITT Application in Kubernetes
# Usage: ./monitor.sh [command]

set -e

NAMESPACE="crud-itt"
APP_LABEL="app=fastapi-crud"

# Function to show help
show_help() {
    echo "CRUD-ITT Kubernetes Monitor"
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  status    Show deployment status (default)"
    echo "  logs      Show application logs"
    echo "  pods      Show pod information"
    echo "  events    Show recent events"
    echo "  resources Show resource usage"
    echo "  port      Port forward to local machine"
    echo "  shell     Get shell access to a pod"
    echo "  help      Show this help message"
}

# Function to show deployment status
show_status() {
    echo "📊 CRUD-ITT Deployment Status"
    echo "============================="
    
    kubectl get all -n "$NAMESPACE" -l "$APP_LABEL"
    
    echo ""
    echo "🔗 Service Details:"
    kubectl describe svc crud-itt-service -n "$NAMESPACE"
    
    echo ""
    echo "🌐 Ingress Details:"
    kubectl describe ingress crud-itt-ingress -n "$NAMESPACE"
}

# Function to show logs
show_logs() {
    echo "📝 Application Logs"
    echo "=================="
    
    # Check if -f flag should be added for follow
    if [[ "$1" == "-f" ]] || [[ "$1" == "--follow" ]]; then
        kubectl logs -l "$APP_LABEL" -n "$NAMESPACE" -f --tail=100
    else
        kubectl logs -l "$APP_LABEL" -n "$NAMESPACE" --tail=50
        echo ""
        echo "💡 Tip: Use '$0 logs -f' to follow logs in real-time"
    fi
}

# Function to show pod information
show_pods() {
    echo "🏃 Pod Information"
    echo "=================="
    
    kubectl get pods -n "$NAMESPACE" -l "$APP_LABEL" -o wide
    
    echo ""
    echo "📋 Pod Details:"
    kubectl describe pods -n "$NAMESPACE" -l "$APP_LABEL"
}

# Function to show events
show_events() {
    echo "📅 Recent Events"
    echo "================"
    
    kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' --field-selector involvedObject.kind=Pod
}

# Function to show resource usage
show_resources() {
    echo "💾 Resource Usage"
    echo "================="
    
    # Check if metrics-server is available
    if kubectl top nodes &> /dev/null; then
        echo "📊 Node Resources:"
        kubectl top nodes
        
        echo ""
        echo "📊 Pod Resources:"
        kubectl top pods -n "$NAMESPACE" -l "$APP_LABEL"
    else
        echo "⚠️  Metrics server not available. Showing resource requests/limits:"
        kubectl describe pods -n "$NAMESPACE" -l "$APP_LABEL" | grep -E "(Requests|Limits):" -A 2
    fi
}

# Function to port forward
port_forward() {
    echo "🔌 Setting up port forwarding..."
    echo "Application will be available at http://localhost:8000"
    echo "Press Ctrl+C to stop"
    
    kubectl port-forward svc/crud-itt-service 8000:80 -n "$NAMESPACE"
}

# Function to get shell access
get_shell() {
    echo "🐚 Getting shell access to pod..."
    
    # Get the first running pod
    POD_NAME=$(kubectl get pods -n "$NAMESPACE" -l "$APP_LABEL" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    if [ -z "$POD_NAME" ]; then
        echo "❌ No running pods found"
        exit 1
    fi
    
    echo "Connecting to pod: $POD_NAME"
    kubectl exec -it "$POD_NAME" -n "$NAMESPACE" -- /bin/bash || kubectl exec -it "$POD_NAME" -n "$NAMESPACE" -- /bin/sh
}

# Main function
main() {
    local command=${1:-status}
    
    case $command in
        status)
            show_status
            ;;
        logs)
            show_logs "$2"
            ;;
        pods)
            show_pods
            ;;
        events)
            show_events
            ;;
        resources)
            show_resources
            ;;
        port)
            port_forward
            ;;
        shell)
            get_shell
            ;;
        help)
            show_help
            ;;
        *)
            echo "❌ Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Run main function
main "$@"