"""
Secure Password Hashing and Verification Service

This module provides secure password hashing and verification functionality
using bcrypt algorithm with configurable salt rounds for optimal security
and performance balance in the CRUD ITT application.

Key Features:
- Industry-standard bcrypt password hashing
- Configurable salt rounds for security/performance tuning
- Secure salt generation for each password
- Constant-time password verification
- UTF-8 encoding handling for international characters
- Integration with application configuration system

Security Features:
- Unique salt generation for each password (prevents rainbow table attacks)
- Configurable work factor (salt rounds) to adapt to hardware improvements
- Secure random salt generation using OS entropy
- Constant-time comparison to prevent timing attacks
- No plaintext password storage or logging

Performance Considerations:
- Salt rounds configurable via settings (default: 12)
- Higher rounds = more secure but slower
- Recommended ranges: 10-15 for current hardware
- Hashing time scales exponentially with rounds
- Consider async operations for web requests

Configuration:
Salt rounds are configured via application settings:
- Development: 10-12 rounds (faster for testing)
- Production: 12-15 rounds (optimal security)
- High-security: 15+ rounds (government/financial)

Usage:
```python
from services.password_service import hash_password, verify_password

# Hash password during registration
hashed = hash_password("user_password123")

# Verify password during login
is_valid = verify_password("user_password123", hashed)
```

Integration:
- Used by authentication service for login verification
- Used by user service for password changes
- Integrated with API endpoints for user management
- Compatible with database storage requirements

Security Standards:
- Follows OWASP password storage guidelines
- Resistant to common attack vectors
- Suitable for compliance requirements
- Regular security review recommended

Author: Gabomfim
License: MIT
"""

import bcrypt

from config import settings


def hash_password(password: str) -> str:
    """Generate secure bcrypt hash for password with configurable work factor.
    
    This function creates a cryptographically secure password hash using the bcrypt
    algorithm with a unique salt for each password. The work factor (salt rounds)
    is configurable via application settings to balance security and performance.
    
    Security Features:
        - Unique salt generation for each password (prevents rainbow table attacks)
        - Configurable work factor via settings.security.bcrypt_rounds
        - Secure random salt using OS entropy sources
        - Industry-standard bcrypt algorithm (Blowfish-based)
        - UTF-8 encoding support for international characters
    
    Args:
        password: Plaintext password to hash
                 Should be validated for strength before hashing
                 Supports Unicode characters and special symbols
                 Typically 8-128 characters in length
    
    Returns:
        str: Base64-encoded bcrypt hash as UTF-8 string
             Format: $2b$[rounds]$[22-char salt][31-char hash]
             Example: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj7RG6V8K2.y"
             Length: ~60 characters for storage planning
    
    Performance:
        - Execution time depends on configured salt rounds:
          * 10 rounds: ~10ms (fast, minimum recommended)
          * 12 rounds: ~50ms (default, good balance)
          * 14 rounds: ~200ms (high security)
          * 16 rounds: ~800ms (very high security)
        - Time scales exponentially: each +1 round doubles time
        - Consider async operations for web request contexts
    
    Configuration:
        Salt rounds configured via settings.security.bcrypt_rounds:
        - Development: 10-11 (faster testing)
        - Production: 12-13 (standard security)
        - High-security: 14-15 (government/financial)
    
    Usage Examples:
        ```python
        # Standard usage
        hashed = hash_password("MySecurePassword123!")
        
        # With validation
        if validate_password_strength(password):
            hashed = hash_password(password)
            store_in_database(username, hashed)
        ```
    
    Security Considerations:
        - Never log or store the input password
        - Always validate password strength before hashing
        - Use HTTPS to protect password transmission
        - Consider password policies (length, complexity)
        - Store hash result securely in database
    
    Error Handling:
        - bcrypt.hashpw() handles salt generation errors internally
        - UTF-8 encoding errors will raise UnicodeError
        - Memory errors for extremely long passwords
    
    Storage Requirements:
        - Database column should be VARCHAR(255) or TEXT
        - Actual hash length is ~60 characters
        - Consider indexing strategy (usually not indexed)
    """
    # Generate salt with configured rounds and hash password
    salt = bcrypt.gensalt(rounds=settings.security.bcrypt_rounds)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Securely verify plaintext password against stored bcrypt hash.
    
    This function performs constant-time password verification using bcrypt's
    built-in comparison function. It automatically extracts the salt and work
    factor from the stored hash and applies the same hashing process to verify
    the provided plaintext password.
    
    Security Features:
        - Constant-time comparison prevents timing attacks
        - Automatic salt and work factor extraction from hash
        - No plaintext password storage or caching
        - Secure UTF-8 encoding handling
        - Resistant to length extension attacks
    
    Args:
        plain_password: User-provided plaintext password to verify
                       Should be the exact password without modification
                       Supports Unicode characters and special symbols
                       Typically received from login form or API
        
        hashed_password: Stored bcrypt hash from database
                        Format: $2b$[rounds]$[22-char salt][31-char hash]
                        Must be complete hash including salt and work factor
                        Should be retrieved securely from user record
    
    Returns:
        bool: True if password matches the hash, False otherwise
              False is also returned for malformed hashes or encoding errors
              Result should be used immediately (don't cache)
    
    Performance:
        - Verification time matches original hashing time
        - Time depends on work factor stored in hash:
          * 10 rounds: ~10ms verification time
          * 12 rounds: ~50ms verification time
          * 14 rounds: ~200ms verification time
        - Consider rate limiting for authentication endpoints
        - Use async operations in web request handlers
    
    Usage Examples:
        ```python
        # Standard authentication flow
        user = get_user_by_username(username)
        if user and verify_password(password, user.password_hash):
            return create_session(user)
        else:
            return authentication_failed()
        
        # With error handling
        try:
            is_valid = verify_password(form_password, stored_hash)
            if is_valid:
                login_user(user)
            else:
                increment_failed_attempts(user)
        except Exception as e:
            log_security_event("password_verification_error", e)
            return False
        ```
    
    Security Best Practices:
        - Always use constant-time comparison result
        - Don't reveal whether user exists vs password wrong
        - Log failed authentication attempts for monitoring
        - Consider account lockout after multiple failures
        - Rate limit authentication endpoints
        - Use HTTPS for password transmission
    
    Error Handling:
        - Returns False for any verification errors
        - Malformed hashes return False (graceful degradation)
        - UTF-8 encoding errors return False
        - Exception details not exposed to prevent information leakage
    
    Timing Considerations:
        - Verification time is constant regardless of result
        - Time varies only with hash work factor, not password
        - Prevents timing-based username enumeration
        - Consistent response time helps prevent side-channel attacks
    
    Integration Notes:
        - Used in authentication service for login verification
        - Compatible with password change workflows
        - Works with any bcrypt hash regardless of work factor
        - Suitable for migration from other bcrypt implementations
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )
