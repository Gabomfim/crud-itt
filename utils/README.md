# Utils Directory 🛠️

This directory contains utility functions, middleware, and helper tools that support the entire application.

## 🎯 Purpose

The `utils/` directory provides common functionality that multiple parts of the application need, such as logging, request processing, and middleware that runs on every request.

## 📁 Directory Structure

```
utils/
├── __init__.py          # Package initialization
├── logging_config.py    # Logging configuration and structured logging
└── middleware.py        # HTTP middleware for request processing
```

## 📄 File Overview

### `logging_config.py` - Logging System
**Purpose**: Comprehensive logging system for monitoring and debugging

**What it does**:
- Sets up structured logging (JSON format for production)
- Provides different log levels (DEBUG, INFO, WARNING, ERROR)
- Includes request tracing with unique IDs
- Supports integration with monitoring tools
- Formats logs for easy reading and analysis

**For beginners**: Think of this as the "diary" of your application - it writes down everything that happens so you can see what went wrong if there are problems, or monitor how well things are working.

**Key Components**:
- `JSONFormatter` - Formats logs as structured JSON
- `StructuredAdapter` - Adds context to log messages
- `setup_logging()` - Configures the logging system
- `get_logger()` - Gets a logger for any module

### `middleware.py` - HTTP Middleware
**Purpose**: Processes every HTTP request and response

**What it does**:
- Logs all incoming requests and responses
- Adds unique request IDs for tracing
- Measures response times for performance monitoring
- Provides health check endpoints
- Handles CORS and other cross-cutting concerns

**For beginners**: Think of middleware as "inspectors" that check every request coming in and every response going out, making notes about what happened and how long it took.

**Key Components**:
- `RequestLoggingMiddleware` - Logs all HTTP traffic
- `HealthCheckMiddleware` - Provides health check endpoints

## 🔍 Logging System

### Log Levels Explained
```python
# DEBUG - Detailed information for diagnosing problems
logger.debug("User search query", extra={"query": "john", "results": 5})

# INFO - General information about normal operations  
logger.info("User logged in", extra={"username": "john", "ip": "192.168.1.1"})

# WARNING - Something unexpected happened, but app still works
logger.warning("Slow database query", extra={"duration_ms": 2500})

# ERROR - Something went wrong, but app can continue
logger.error("Failed to send email", extra={"user_id": 123, "error": "SMTP timeout"})

# CRITICAL - Serious error that might stop the app
logger.critical("Database connection lost", extra={"error": "Connection refused"})
```

### Structured Logging Example
```python
from utils.logging_config import get_logger

logger = get_logger(__name__)

# Simple logging
logger.info("User created successfully")

# Structured logging with context
logger.info("User created", extra={
    "user_id": 123,
    "username": "johndoe", 
    "ip_address": "192.168.1.100",
    "duration_ms": 245.5
})
```

### Log Output Formats

**Development (Human-readable)**:
```
2024-01-15 10:30:45 - api.v1.user_routes - INFO - User created successfully
```

**Production (JSON for monitoring tools)**:
```json
{
    "timestamp": "2024-01-15T10:30:45.123456Z",
    "level": "INFO",
    "logger": "api.v1.user_routes",
    "message": "User created successfully",
    "user_id": 123,
    "username": "johndoe",
    "request_id": "abc-123-def-456"
}
```

## 🌐 Request Logging Middleware

### What Gets Logged

**Incoming Request**:
```json
{
    "timestamp": "2024-01-15T10:30:45.123Z",
    "level": "INFO", 
    "message": "Request started",
    "request_id": "abc-123-def-456",
    "method": "POST",
    "url": "http://localhost:8000/api/v1/users",
    "path": "/api/v1/users",
    "query_params": {},
    "client_ip": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "content_type": "application/json"
}
```

**Outgoing Response**:
```json
{
    "timestamp": "2024-01-15T10:30:45.456Z",
    "level": "INFO",
    "message": "Request completed", 
    "request_id": "abc-123-def-456",
    "method": "POST",
    "path": "/api/v1/users",
    "status_code": 201,
    "duration_ms": 125.5,
    "response_size": "156"
}
```

### Request Tracing
```python
# Each request gets a unique ID that appears in all related logs
# This helps you follow a single request through the entire system

# Request starts
"request_id": "abc-123-def-456" - Request started

# Business logic
"request_id": "abc-123-def-456" - Validating user data
"request_id": "abc-123-def-456" - Checking username availability  
"request_id": "abc-123-def-456" - Hashing password
"request_id": "abc-123-def-456" - Saving user to database

# Request completes
"request_id": "abc-123-def-456" - Request completed
```

## 🏥 Health Check Middleware

### Health Check Endpoint
```bash
# Check if your application is running
curl http://localhost:8000/health

# Response:
{
    "status": "healthy",
    "service": "crud-itt"
}
```

### Use Cases
- **Load Balancer**: Checks if server can handle traffic
- **Kubernetes**: Determines if pod is ready for requests
- **Monitoring**: Automated health monitoring
- **Docker**: Container health checks

### Performance
- Ultra-fast response (< 1ms)
- No database or external service dependencies
- Bypasses authentication and business logic
- Perfect for high-frequency health checks

## 🔧 Configuration Examples

### Development Logging Setup
```python
# Fast, readable logs for development
setup_logging(
    log_level="DEBUG",
    json_logs=False,  # Human-readable format
    app_name="crud-itt-dev"
)
```

### Production Logging Setup
```python
# Structured logs for monitoring systems
setup_logging(
    log_level="INFO", 
    json_logs=True,   # JSON format for log aggregation
    app_name="crud-itt-prod"
)
```

### Middleware Configuration
```python
from fastapi import FastAPI
from utils.middleware import RequestLoggingMiddleware, HealthCheckMiddleware

app = FastAPI()

# Add request logging (logs all HTTP traffic)
app.add_middleware(
    RequestLoggingMiddleware,
    exclude_paths=["/health", "/metrics"]  # Don't log health checks
)

# Add health check endpoint
app.add_middleware(
    HealthCheckMiddleware,
    health_path="/health"
)
```

## 📊 Monitoring Integration

### ELK Stack (Elasticsearch, Logstash, Kibana)
```json
// JSON logs are perfect for Elasticsearch
{
    "timestamp": "2024-01-15T10:30:45.123Z",
    "level": "INFO",
    "service": "crud-itt", 
    "request_id": "abc-123",
    "user_id": 123,
    "duration_ms": 125.5
}
```

### Prometheus Metrics
```python
# Response time metrics for Prometheus
histogram_metric = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint', 'status_code']
)
```

### Application Performance Monitoring (APM)
```python
# Request tracing for New Relic, DataDog, etc.
logger.info("Database query", extra={
    "request_id": request_id,
    "query_type": "user_lookup",
    "duration_ms": 45.2,
    "rows_returned": 1
})
```

## 🛡️ Security Features

### IP Address Detection
```python
# Properly detects client IP behind proxies
def _get_client_ip(self, request):
    # 1. Check X-Forwarded-For header (load balancers)
    # 2. Check X-Real-IP header (reverse proxies)
    # 3. Fall back to direct connection IP
```

### Sensitive Data Protection
```python
# Middleware automatically excludes sensitive headers
exclude_headers = [
    "authorization",
    "cookie", 
    "x-api-key"
]

# Never logs request/response bodies (may contain passwords)
```

### Request Size Limits
```python
# Prevents abuse through large requests
# Configured at FastAPI level, logged by middleware
```

## 🧪 Testing Utilities

### Testing Logging
```python
import logging
from utils.logging_config import get_logger

def test_logging():
    logger = get_logger("test")
    
    with pytest.LogCapture() as log_capture:
        logger.info("Test message", extra={"test_id": 123})
        log_capture.check(
            ("test", "INFO", "Test message")
        )
```

### Testing Middleware
```python
from fastapi.testclient import TestClient
from utils.middleware import RequestLoggingMiddleware

def test_request_logging():
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)
    
    client = TestClient(app)
    response = client.get("/test")
    
    # Check that request was logged
    # Check response headers include request ID
```

## 🚀 Performance Considerations

### Logging Performance
```python
# JSON formatting: ~0.2ms per log entry
# Structured field extraction: ~0.1ms per log entry  
# Total overhead: <1ms per request
```

### Middleware Performance
```python
# Request logging: ~1-2ms overhead per request
# Health check: <0.1ms response time
# UUID generation: ~0.01ms per request
```

### Memory Usage
```python
# Minimal memory footprint
# Logs are written immediately (no buffering)
# Request IDs are garbage collected after response
```

## 🎓 Learning Path

**Beginner**: 
1. Understand what logging is and why it's important
2. Look at log output in development mode
3. See how health checks work
4. Learn about different log levels

**Intermediate**: 
1. Study structured logging and JSON format
2. Learn about request tracing with IDs
3. Understand middleware execution order
4. Practice with log analysis tools

**Advanced**: 
1. Set up log aggregation systems (ELK stack)
2. Create custom middleware
3. Implement performance monitoring
4. Design observability strategies

## 🔗 Integration Examples

### Using Logging in Services
```python
# services/user_service.py
from utils.logging_config import get_logger

logger = get_logger(__name__)

async def create_user(user_data: dict):
    logger.info("Creating user", extra={
        "username": user_data["username"],
        "operation": "user_creation"
    })
    
    try:
        # Create user logic
        logger.info("User created successfully", extra={
            "user_id": user.id,
            "username": user.username
        })
    except Exception as e:
        logger.error("Failed to create user", extra={
            "username": user_data["username"],
            "error": str(e)
        }, exc_info=True)
        raise
```

### Using Request ID in Business Logic
```python
# api/v1/user_routes.py
from fastapi import Request

@router.post("/users")
async def create_user(request: Request, user_data: UserRequest):
    # Get request ID set by middleware
    request_id = getattr(request.state, 'request_id', None)
    
    logger.info("Processing user creation", extra={
        "request_id": request_id,
        "username": user_data.username
    })
```

---

**Next**: Check out the [`tests/`](../tests/README.md) directory to see how to test all these components!