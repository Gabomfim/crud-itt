# Code Quality and Formatting Setup

This project uses automated code formatting and quality checks that run before every commit.

## Tools Used

### 🎨 **Black** - Code Formatter
- Automatically formats Python code to consistent style
- Line length: 88 characters
- Runs on every commit

### 🔧 **isort** - Import Sorter  
- Automatically sorts and organizes imports
- Compatible with Black formatting

### 📏 **Flake8** - Linter
- Checks code quality and style issues
- Enforces PEP 8 compliance
- Compatible with Black (ignores E203, W503)

### 🔍 **mypy** - Static Type Checker
- Performs static type analysis on Python code
- Catches type-related errors before runtime
- Ensures type annotations are correct and consistent
- Configured with strict type checking options

### ✅ **Pre-commit Hooks**
- Runs automatically before git commits
- Prevents committing poorly formatted code
- Includes additional checks (trailing whitespace, file endings, etc.)

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Pre-commit Hooks
```bash
pre-commit install
```

### 3. (Optional) Install Pre-push Hook for Tests
```bash
pre-commit install --hook-type pre-push
```

## Manual Usage

### Format Code with Black
```bash
# Format all Python files
black .

# Format specific file
black app.py

# Check what would be formatted (dry run)
black --check .
```

### Sort Imports with isort
```bash
# Sort all imports
isort .

# Check what would be changed
isort --check-only .
```

### Check Code Quality with Flake8
```bash
# Check all files
flake8

# Check specific file
flake8 app.py
```

### Type Check with mypy
```bash
# Check all files
mypy .

# Check specific file  
mypy app.py

# Check with verbose output
mypy --verbose .
```

### Run All Pre-commit Hooks Manually
```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

## What Happens on Commit

When you run `git commit`, the following happens automatically:

1. **Black** formats your Python code
2. **isort** organizes your imports
3. **Flake8** checks for code quality issues
4. **mypy** performs static type checking
5. **Pre-commit hooks** run additional checks:
   - Remove trailing whitespace
   - Fix end-of-file formatting
   - Validate YAML/JSON/TOML files
   - Check for large files
   - Detect merge conflicts
   - Remove debug statements

If any tool finds issues and fixes them, the commit will be stopped. You'll need to review the changes and commit again.

## Configuration Files

- **`.pre-commit-config.yaml`** - Pre-commit hook configuration
- **`pyproject.toml`** - Black formatter and mypy configuration
- **`requirements.txt`** - Includes all formatting and type checking tools

## Benefits

✅ **Consistent Code Style** - All code follows the same formatting rules  
✅ **Automatic Formatting** - No manual formatting needed  
✅ **Quality Assurance** - Catches common issues before they reach the repository  
✅ **Type Safety** - Static type checking prevents runtime type errors  
✅ **Team Collaboration** - Everyone's code looks the same  
✅ **Time Saving** - No debates about formatting in code reviews  

## Skipping Hooks (Emergency Only)

If you need to skip pre-commit hooks in an emergency:
```bash
git commit --no-verify -m "Emergency commit"
```

**Note**: This should be used sparingly and followed up with proper formatting.

## mypy Configuration

The project includes a `mypy.ini` configuration file with strict type checking enabled:
- All functions must have type annotations
- No implicit Optional types allowed
- Warnings for unused imports and redundant casts
- Strict equality checking

mypy runs automatically in CI/CD but can also be run locally:
```bash
mypy .
```