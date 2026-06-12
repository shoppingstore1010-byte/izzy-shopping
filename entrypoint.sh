#!/bin/bash
set -e

# Use PORT environment variable if set, otherwise default to 8000
PORT=${PORT:-8000}

# Run gunicorn with the PORT variable
exec gunicorn izzy_signature.wsgi:application \
    --bind 0.0.0.0:${PORT} \
    --workers 3 \
    --timeout 120
