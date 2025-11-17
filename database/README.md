# Database Directory 🗄️

This directory handles all database connections, models, and initialization for the application.

## 🎯 Purpose

The `database/` directory manages data persistence, providing the bridge between your application and the database where user information is stored.

## 📁 Directory Structure

```
database/
├── __init__.py          # Package initialization
├── connection.py        # Database connection and ORM models
└── init.py             # Database initialization with sample data
```

## 📄 File Overview

### `connection.py` - Database Connection & Models
**Purpose**: Sets up database connection and defines data structure

**What it does**:
- Creates connection to database (SQLite, PostgreSQL, etc.)
- Defines the User table structure
- Provides session management for database operations
- Handles connection pooling for better performance

**For beginners**: Think of this as the "blueprint" that tells the database what a user looks like (username, password, age, etc.) and how to connect to the database.

**Key Components**:
- `async_engine` - The database connection
- `AsyncSessionLocal` - Factory for database sessions
- `Base` - Foundation for all database models
- `User` - The user table definition
- `init_database()` - Creates tables if they don't exist
- `get_db()` - Provides database sessions to API endpoints

### `init.py` - Database Initialization
**Purpose**: Sets up initial data for development and testing

**What it does**:
- Creates sample users if database is empty
- Provides initial data for development
- Shows how to create users programmatically

**For beginners**: This is like a "setup script" that adds some example users to your database so you have something to work with during development.

**⚠️ Important**: This file contains sample passwords and should only be used for development!

## 🏗️ Database Schema

### User Table Structure
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique user ID
    username VARCHAR(30) UNIQUE NOT NULL,  -- Login username
    password VARCHAR(255) NOT NULL,        -- Hashed password
    age INTEGER NOT NULL,                  -- User age
    description VARCHAR(200) DEFAULT ''    -- Profile description
);
```

### Database Constraints
- **Username**: Must be unique, 3-30 characters, not empty
- **Password**: Must be 60+ characters (for bcrypt hash)
- **Age**: Must be 1-120 years old
- **Description**: Maximum 200 characters, optional

### Indexes
- Primary key on `id` (automatic)
- Unique index on `username` (for fast login lookups)

## 💾 Supported Databases

### SQLite (Default - Development)
```python
DATABASE_URL = "sqlite+aiosqlite:///./database/users.db"
```
**Best for**: Development, testing, small applications

**Pros**: 
- No setup required
- File-based, easy to backup
- Perfect for learning

**Cons**: 
- Single writer at a time
- Not suitable for high-traffic production

### PostgreSQL (Recommended - Production)
```python
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/crud_itt"
```
**Best for**: Production applications

**Pros**: 
- Handles multiple users simultaneously
- Advanced features and performance
- Industry standard

**Cons**: 
- Requires separate PostgreSQL server
- More complex setup

### MySQL (Alternative - Production)
```python
DATABASE_URL = "mysql+aiomysql://user:pass@localhost/crud_itt"
```
**Best for**: Production applications, legacy systems

## 🔄 Database Operations

### Creating a User
```python
from database.connection import User, get_db

async def create_user_example():
    async with get_db() as session:
        new_user = User(
            username="johndoe",
            password="hashed_password_here",
            age=25,
            description="Software developer"
        )
        session.add(new_user)
        await session.commit()
        return new_user
```

### Finding a User
```python
from sqlalchemy import select

async def find_user_example():
    async with get_db() as session:
        stmt = select(User).where(User.username == "johndoe")
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        return user
```

### Updating a User
```python
async def update_user_example():
    async with get_db() as session:
        stmt = select(User).where(User.username == "johndoe")
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            user.description = "Senior Software Developer"
            await session.commit()
        return user
```

### Deleting a User
```python
async def delete_user_example():
    async with get_db() as session:
        stmt = select(User).where(User.username == "johndoe")
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            await session.delete(user)
            await session.commit()
        return True
```

## ⚡ Connection Pooling

### How It Works
```python
# Database engine configuration
async_engine = create_async_engine(
    settings.database.url,
    echo=settings.database.echo,           # Log SQL queries
    pool_size=settings.database.pool_size, # Number of connections
    max_overflow=settings.database.max_overflow  # Extra connections
)
```

### Pool Settings
- **pool_size**: Normal number of connections (default: 10)
- **max_overflow**: Extra connections when busy (default: 20)
- **pool_timeout**: Wait time for available connection
- **pool_recycle**: Reset connections after time period

**For beginners**: Connection pooling is like having multiple phone lines to the database instead of just one, so multiple users can access data simultaneously without waiting.

## 🛠️ Database Initialization

### First Time Setup
```bash
# Run initialization script
python -m database.init
```

### What Gets Created
1. **Database file**: `database/users.db` (for SQLite)
2. **Users table**: With all constraints and indexes
3. **Sample users**: 
   - Username: `lavinia`, Password: `Lavinia123!`
   - Username: `gabriel`, Password: `Gabriel456@`

### Manual Initialization
```python
from database.connection import init_database

# Initialize database programmatically
await init_database()
```

## 🔧 Session Management

### How Sessions Work
```python
# Get a database session
async def some_operation():
    async with get_db() as session:
        # Do database operations here
        user = await session.get(User, 1)
        # Session automatically closed when done
```

### Session Lifecycle
1. **Create** - New session from pool
2. **Use** - Perform database operations
3. **Commit/Rollback** - Save or discard changes
4. **Close** - Return connection to pool

### Best Practices
- Always use `async with` for sessions
- Commit explicitly for data changes
- Handle exceptions properly
- Don't share sessions between requests

## 🛡️ Security Features

### Password Storage
```python
# ❌ NEVER store plaintext passwords
user.password = "my_password"

# ✅ Always store hashed passwords
from services.password_service import hash_password
user.password = hash_password("my_password")
```

### SQL Injection Prevention
```python
# ✅ SQLAlchemy ORM prevents SQL injection
stmt = select(User).where(User.username == user_input)  # Safe

# ❌ Raw SQL can be dangerous
query = f"SELECT * FROM users WHERE username = '{user_input}'"  # Dangerous
```

## 🔍 Database Tools

### View Database Contents (SQLite)
```bash
# Install SQLite command line tool
sqlite3 database/users.db

# View tables
.tables

# View users
SELECT * FROM users;

# Exit
.quit
```

### Database Migration
For schema changes in production:
1. Use database migration tools (Alembic)
2. Test migrations on staging first
3. Backup database before changes
4. Plan for rollback if needed

## 🐛 Common Issues & Solutions

### Issue: "Database is locked"
**Cause**: Multiple processes trying to write to SQLite
**Solution**: 
- Use connection pooling
- Ensure sessions are properly closed
- Consider PostgreSQL for production

### Issue: "Table doesn't exist"
**Cause**: Database not initialized
**Solution**: Run `await init_database()` or `python -m database.init`

### Issue: "Connection refused"
**Cause**: Database server not running (PostgreSQL/MySQL)
**Solution**: Start your database server and check connection string

## 🎓 Learning Path

**Beginner**: 
1. Understand what each file does
2. Look at the User model structure
3. Try running the initialization script
4. Use SQLite browser to view data

**Intermediate**: 
1. Study the async session patterns
2. Learn about database constraints
3. Practice with different query patterns
4. Understand connection pooling

**Advanced**: 
1. Set up PostgreSQL connection
2. Learn about database migrations
3. Study performance optimization
4. Implement custom database operations

---

**Next**: Check out the [`models/`](../models/README.md) directory to see how data validation works!