# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /app
COPY requirements.txt .

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt && \
    # Install gunicorn for production
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels gunicorn psycopg2-binary

# Stage 2: Production runtime
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies for psycopg2 (PostgreSQL)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy wheels from builder and install
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# Copy application code
COPY . .

# Ensure upload directories exist
RUN mkdir -p app/static/uploads/tickets app/static/uploads/certificates app/static/uploads/qr_codes

# Set environment variables for production
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV DISABLE_SCHEDULER=True

EXPOSE 8000

# Run with Gunicorn (4 workers)
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "run:app"]
