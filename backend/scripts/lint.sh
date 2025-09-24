#!/bin/bash

# Format and lint script for the backend
echo "🚀 Running Ruff formatter..."
poetry run ruff format src/

echo "🔎 Running Ruff linter..."
poetry run ruff check src/ --fix

echo "🔍 Running type checker..."
poetry run mypy src/

echo "✅ All checks completed!"