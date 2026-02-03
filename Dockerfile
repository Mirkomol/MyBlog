# Simple Dockerfile - SQLite (No PostgreSQL dependencies!)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_CONFIG=production

# Set work directory
WORKDIR /app

# Install Python dependencies (no system deps needed for SQLite!)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for data persistence
RUN mkdir -p /app/data /app/app/static/uploads

# Expose port
EXPOSE 5000

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "--workers", "2", "wsgi:app"]
