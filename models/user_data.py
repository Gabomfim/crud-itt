"""
Legacy User Data Module

This module contains hardcoded sample user data that appears to be from an
earlier version of the application before database integration was implemented.

SECURITY WARNING: This module contains plaintext passwords and should not be
used in any production or security-sensitive context.

DEPRECATION NOTICE: This module appears to be legacy code that predates the
database implementation. Modern user data should be managed through:
- Database operations via SQLAlchemy ORM models
- API endpoints for user creation and management
- Proper authentication with hashed passwords

Current Issues:
- Plaintext passwords (major security vulnerability)
- Hardcoded data instead of database persistence
- Portuguese language mixed with English codebase
- No validation or error handling

Recommended Actions:
1. Remove this module from production code
2. Use database/init.py for sample data creation
3. Ensure all passwords are properly hashed
4. Implement proper user management via API endpoints

This module is preserved for historical reference but should not be used
in the current application architecture.

Author: Gabomfim (Legacy)
License: MIT
Status: DEPRECATED - DO NOT USE
"""

from models.user import User

# DEPRECATED: Legacy hardcoded user data with security vulnerabilities
# These users contain plaintext passwords and should NOT be used
# Use database/init.py for proper sample data creation

# WARNING: Plaintext passwords - SECURITY VULNERABILITY
lavinia = User(username="lavinia", password="1234", age=16, description="Odeio sushi")
gabriel = User(
    username="gabriel", password="5678", age=26, description="Gosto de morango"
)

# DEPRECATED: In-memory user list - use database instead
lista_de_usuarios = [lavinia, gabriel]
