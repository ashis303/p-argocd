# Use official Python runtime as base image
# Alpine Linux keeps the image size small
FROM python:3.11-alpine

# Set working directory in container
WORKDIR /app

# Install dependencies
# Copy requirements first for better Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create directory for secrets mount point
# The CSI driver will mount secrets here at runtime
RUN mkdir -p /mnt/secrets

# Expose port 8080
EXPOSE 8080

# Run application using Gunicorn in production
# --bind 0.0.0.0:8080: Listen on all interfaces
# --workers 2: Number of worker processes
# --timeout 120: Worker timeout in seconds
# --access-logfile -: Log to stdout
# --error-logfile -: Log errors to stderr
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
