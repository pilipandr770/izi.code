#!/bin/bash
# startup.sh - Script to start the application with proper logging

echo "Starting application with gunicorn..."
echo "Environment: $(printenv | grep -E 'FLASK|DATABASE|OPENAI|PYTHON' | grep -v PASSWORD)"
echo "Using Python $(python --version)"

# Create data directories if they don't exist
mkdir -p app/static/uploads

# Start gunicorn with reduced workers to save memory
export PYTHONUNBUFFERED=1
exec gunicorn --config gunicorn.conf.py wsgi:app
