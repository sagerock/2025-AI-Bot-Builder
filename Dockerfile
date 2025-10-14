FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directory for SQLite database
RUN mkdir -p /app/data

# Expose port (Railway will inject PORT env var)
EXPOSE 8000

# Run the application using Python script that reads PORT from environment
# Use shell form to ensure environment variables are available
CMD python railway_start.py
