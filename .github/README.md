# GitHub Actions Configuration
# This directory contains automated workflows for:
# 
# 1. ci.yml - Main CI/CD pipeline
#    - Runs on push to main/develop branches
#    - Runs on pull requests to main/develop
#    - Tests across multiple Python versions (3.8-3.12)
#    - Performs linting, formatting checks, and security scanning
#    - Builds and tests Docker images
#
# 2. dev-checks.yml - Development workflow
#    - Quick checks for pull requests
#    - Provides fast feedback during development
#    - Posts coverage reports as PR comments
#
# 3. release.yml - Release workflow
#    - Triggered on version tags (v*)
#    - Creates release artifacts
#    - Performs security audits
#    - Uploads assets to GitHub releases
#
# Local Development:
# To run the same checks locally before pushing:
#   pytest                    # Run tests
#   black .                   # Format code
#   isort .                   # Sort imports
#   flake8 .                  # Lint code
#   mypy .                    # Type check
#   safety check              # Security scan
#   bandit -r . -x tests/     # Static security analysis
#
# Pre-commit hooks are also configured to run these checks automatically.