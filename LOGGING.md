# Logging Documentation

This document describes the comprehensive logging system implemented in the FastAPI CRUD application.

## Overview

The application implements structured logging with support for both human-readable and JSON formats, making it suitable for both development and production environments.

## Features

### ✅ Core Logging Features
- **Structured Logging**: JSON format for production, human-readable for development
- **Request/Response Logging**: Automatic HTTP request tracking with unique request IDs
- **Error Tracking**: Comprehensive exception logging with stack traces
- **Performance Monitoring**: Request duration tracking
- **Health Checks**: Built-in health check endpoint with minimal logging overhead

### ✅ Logging Components

1. **Logging Configuration** (`utils/logging_config.py`)
   - JSON formatter for structured logs
   - Environment-based configuration
   - Structured adapter for enhanced logging

2. **Request Middleware** (`utils/middleware.py`)
   - Request/response logging with unique IDs
   - Client IP extraction
   - Performance timing
   - Health check middleware

3. **Service Layer Logging**
   - Database operation logging
   - Error handling and recovery
   - User action tracking

4. **Database Logging**
   - Connection and initialization logging
   - Transaction error handling

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `JSON_LOGS` | `false` | Enable JSON formatted logs for production |

### Development vs Production

**Development** (Human-readable):
```
2025-11-16 18:46:15 - crud-itt - INFO - Request started
```

**Production** (JSON):
```json
{
  "timestamp": "2025-11-16T21:46:23.766029Z",
  "level": "INFO", 
  "logger": "crud-itt",
  "message": "Request started",
  "request_id": "abc-123",
  "method": "GET",
  "path": "/api/v1/users"
}
```

## Usage Examples

### Basic Logging
```python
from utils.logging_config import get_logger

logger = get_logger(__name__)

# Simple log
logger.info("User operation completed")

# Structured log with context
logger.info(
    "User created successfully",
    extra={
        "user_id": 123,
        "username": "john_doe",
        "request_id": "abc-123"
    }
)
```

### Error Logging
```python
try:
    # Some operation
    pass
except Exception as e:
    logger.error(
        "Operation failed",
        extra={
            "operation": "create_user",
            "error": str(e)
        },
        exc_info=True  # Include stack trace
    )
```

## Log Fields

### Standard Fields
- `timestamp`: ISO 8601 timestamp in UTC
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `logger`: Logger name (usually module name)
- `message`: Human-readable log message

### Request Fields
- `request_id`: Unique identifier for each request
- `method`: HTTP method (GET, POST, PUT, DELETE)
- `path`: Request path
- `status_code`: HTTP response status
- `duration_ms`: Request processing time in milliseconds
- `client_ip`: Client IP address
- `user_agent`: User agent string

### Application Fields
- `user_id`: User identifier (when available)
- `username`: Username (when available)
- `operation`: Operation being performed
- `error`: Error message
- `error_type`: Exception type name

## Middleware

### Request Logging Middleware
Automatically logs all HTTP requests and responses:

```python
# Added to FastAPI app
app.add_middleware(RequestLoggingMiddleware, exclude_paths=["/health", "/metrics"])
```

**Features:**
- Unique request ID generation
- Request timing
- Client IP extraction
- Automatic error logging
- Response status tracking

### Health Check Middleware
Provides a lightweight health check endpoint:

```python
app.add_middleware(HealthCheckMiddleware, health_path="/health")
```

**Endpoint:** `GET /health`
**Response:**
```json
{
  "status": "healthy",
  "service": "crud-itt"
}
```

## Kubernetes Integration

### Log Collection
The Kubernetes deployment is configured for optimal log collection:

```yaml
# Enables JSON logging in production
env:
  - name: JSON_LOGS
    value: "true"
  - name: LOG_LEVEL
    value: "info"

# Annotations for log collectors
annotations:
  fluentd.active: "true"
  logging.coreos.com/logfile: "/dev/stdout"
```

### Log Aggregation
Logs are written to stdout and can be collected by:
- **Kubernetes**: `kubectl logs -f deployment/crud-itt-app`
- **Fluentd/Fluent Bit**: For centralized logging
- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Prometheus/Grafana**: For metrics and alerting

## Monitoring and Alerting

### Log-based Metrics
Key metrics you can extract from logs:

1. **Request Rate**: Count of request log events
2. **Error Rate**: Count of ERROR level logs
3. **Response Times**: `duration_ms` field values
4. **Status Codes**: Distribution of `status_code` values
5. **User Activity**: Tracking via `user_id` and `username`

### Sample Queries

**Grafana/Prometheus:**
```promql
# Error rate
sum(rate(log_messages_total{level="error"}[5m]))

# Average response time
avg(log_duration_ms{path=~"/api/.*"})
```

**ELK Stack:**
```json
{
  "query": {
    "bool": {
      "must": [
        {"term": {"level": "error"}},
        {"range": {"timestamp": {"gte": "now-1h"}}}
      ]
    }
  }
}
```

## Performance Considerations

### Log Volume Management
- Health checks are excluded from request logging
- SQLAlchemy query logs are set to WARNING level
- uvicorn access logs are minimized

### Async Logging
All logging operations are non-blocking and won't impact request performance.

### Log Rotation
In production, implement log rotation:
```bash
# Example with logrotate
/var/log/crud-itt/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 app app
}
```

## Troubleshooting

### Common Issues

1. **Missing Request IDs**
   - Ensure middleware is properly installed
   - Check middleware order

2. **No JSON Output**
   - Verify `JSON_LOGS=true` environment variable
   - Check logging configuration

3. **High Log Volume**
   - Adjust `LOG_LEVEL` to WARNING or ERROR
   - Add more paths to middleware exclusions

### Debug Mode
Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
poetry run uvicorn app:app --reload
```

### Log Analysis
View structured logs:
```bash
# Follow logs with jq for JSON formatting
kubectl logs -f deployment/crud-itt-app | jq .

# Filter error logs
kubectl logs deployment/crud-itt-app | jq 'select(.level=="ERROR")'

# Monitor request performance
kubectl logs deployment/crud-itt-app | jq 'select(.duration_ms > 1000)'
```

## Best Practices

### Development
1. Use human-readable format (`JSON_LOGS=false`)
2. Set log level to INFO or DEBUG
3. Include context in log messages
4. Don't log sensitive information (passwords, tokens)

### Production
1. Enable JSON logging (`JSON_LOGS=true`)
2. Set appropriate log level (INFO recommended)
3. Implement log aggregation
4. Set up alerting on ERROR logs
5. Monitor request performance via duration logs

### Security
1. Never log passwords or secrets
2. Sanitize user input in logs
3. Use request IDs for user privacy
4. Implement log access controls

## Integration Examples

### Custom Logger Usage
```python
from utils.logging_config import get_logger

class UserService:
    def __init__(self):
        self.logger = get_logger(__name__)
    
    async def create_user(self, user_data):
        self.logger.info(
            "Creating new user",
            extra={"username": user_data.username}
        )
        # ... implementation
        self.logger.info(
            "User created successfully", 
            extra={"user_id": new_user.id}
        )
```

### Request Context
```python
from fastapi import Request

async def some_endpoint(request: Request):
    # Access request ID from middleware
    request_id = getattr(request.state, 'request_id', None)
    
    logger.info(
        "Processing request",
        extra={"request_id": request_id}
    )
```

The logging system provides comprehensive observability for the FastAPI CRUD application, enabling effective monitoring, debugging, and performance analysis across development and production environments.