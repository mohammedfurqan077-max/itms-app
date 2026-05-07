FROM python:3.11-slim

WORKDIR /app

# Install runtime and build dependencies needed by Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies globally so the non-root app user can run them
COPY requirements-railway.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements-railway.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 itms && chown -R itms:itms /app
USER itms

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
