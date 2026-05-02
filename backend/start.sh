#!/bin/bash

# Railway Start Script
# This script runs database migrations and starts the application

set -e  # Exit on error

echo "=========================================="
echo "ITMS Backend - Starting on Railway"
echo "=========================================="
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL is not set"
    exit 1
fi

echo "✓ DATABASE_URL is set"

# Check if SECRET_KEY is set
if [ -z "$SECRET_KEY" ]; then
    echo "ERROR: SECRET_KEY is not set"
    exit 1
fi

echo "✓ SECRET_KEY is set"

# Run database migrations
echo ""
echo "Running database migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✓ Migrations completed successfully"
else
    echo "✗ Migrations failed"
    exit 1
fi

# Start the application
echo ""
echo "Starting application..."
echo "Listening on 0.0.0.0:${PORT:-8000}"
echo ""

exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
