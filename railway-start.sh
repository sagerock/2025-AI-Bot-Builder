#!/bin/bash
# Start the FastAPI application with Railway's PORT environment variable

# Default to port 8000 if PORT is not set
PORT=${PORT:-8000}

echo "Starting uvicorn on port $PORT"
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
