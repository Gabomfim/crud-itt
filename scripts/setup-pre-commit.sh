#!/bin/bash

# Setup pre-commit hooks for the CRUD-ITT project
# This script installs and configures pre-commit hooks to run mypy and other checks

set -e

echo "🔧 Setting up pre-commit hooks for CRUD-ITT project..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "📦 Installing pre-commit..."
    poetry add --group dev pre-commit
fi

# Install the git hook scripts
echo "⚙️  Installing pre-commit hooks..."
poetry run pre-commit install

# Install pre-push hooks (for tests)
echo "⚙️  Installing pre-push hooks..."
poetry run pre-commit install --hook-type pre-push

# Run hooks against all files to ensure they work
echo "🔍 Running pre-commit against all files..."
poetry run pre-commit run --all-files || echo "⚠️  Some hooks failed, but this is expected on first run"

echo ""
echo "✅ Pre-commit hooks installed successfully!"
echo ""
echo "🎯 What happens now:"
echo "  • mypy will run on every commit to check types"
echo "  • flake8 will check code style on every commit"
echo "  • black will format code on every commit" 
echo "  • isort will organize imports on every commit"
echo "  • tests will run on every push"
echo ""
echo "💡 To bypass hooks temporarily: git commit --no-verify"
echo "💡 To run hooks manually: poetry run pre-commit run --all-files"