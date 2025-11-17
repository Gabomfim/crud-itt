"""
Database Initialization and Sample Data Module

This module provides database initialization utilities for development and testing
environments, including sample user creation and database seeding capabilities.

WARNING: This module contains legacy sync code that should be updated to use
async database operations for consistency with the rest of the application.

Key Features:
- Sample user data creation for development
- Database seeding for testing environments
- Initial user account setup with secure passwords
- Development environment bootstrapping

Security Notes:
- Sample users are for development/testing only
- Passwords are properly hashed using bcrypt
- Should not be used in production environments
- Consider using environment-specific seed data

Usage:
This module can be run standalone to initialize the database with sample data:
```bash
python -m database.init
```

Integration:
Can be integrated into application startup or testing workflows for
consistent development environment setup.

TODO: Update to use async database operations for consistency
TODO: Add environment checks to prevent production usage
TODO: Make sample data configurable via environment variables

Author: Gabomfim
License: MIT
"""

from database.connection import AsyncSessionLocal, User
from services.password_service import hash_password


def init_db() -> None:
    """Initialize database with sample user data for development and testing.

    This function creates initial user accounts with secure passwords for
    development and testing purposes. It checks for existing users to avoid
    duplication and provides console output for credential information.

    WARNING: This function uses synchronous database operations which are
    inconsistent with the async architecture of the rest of the application.
    It should be updated to use async/await patterns.

    Sample Users Created:
        - Username: "lavinia", Password: "Lavinia123!", Age: 16
        - Username: "gabriel", Password: "Gabriel456@", Age: 26

    Security Features:
        - Passwords are hashed using secure bcrypt algorithm
        - Strong password patterns with mixed case, numbers, and symbols
        - No plaintext password storage

    Behavior:
        - Only creates users if database is empty (prevents duplicates)
        - Commits transaction only after all users are added
        - Provides console feedback for development workflow
        - Handles database session cleanup

    Raises:
        Database exceptions if connection fails or constraints are violated

    Development Usage:
        ```bash
        # Run standalone
        python -m database.init

        # Or import and call
        from database.init import init_db
        init_db()
        ```

    Integration Notes:
        - Suitable for development environment setup
        - Can be integrated into testing fixtures
        - Should be excluded from production deployments
        - Consider using database migrations for production schema changes

    TODO Items:
        - Convert to async function using AsyncSession
        - Add environment checks to prevent production usage
        - Make sample data configurable
        - Add error handling and logging
        - Integrate with application logging system
    """
    db = AsyncSessionLocal()

    # Check if users already exist
    if db.query(User).count() == 0:
        # Create initial users with hashed passwords
        lavinia = User(
            username="lavinia",
            password=hash_password("Lavinia123!"),
            age=16,
            description="Odeio sushi",
        )
        gabriel = User(
            username="gabriel",
            password=hash_password("Gabriel456@"),
            age=26,
            description="Gosto de morango",
        )

        db.add(lavinia)
        db.add(gabriel)
        db.commit()
        print("Database initialized with sample users")
        print("lavinia password: Lavinia123!")
        print("gabriel password: Gabriel456@")

    db.close()


if __name__ == "__main__":
    init_db()
