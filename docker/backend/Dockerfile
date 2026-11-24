# ── Multi-Stage Python Dockerfile ─────────────────────────────────────────────
# Base Image
FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files & buffer output stream
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WORKDIR=/app

WORKDIR $WORKDIR

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# ── Development Target ────────────────────────────────────────────────────────
FROM base AS development
ENV APP_ENV=development \
    DEBUG=true

COPY backend/requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy backend source code
COPY backend/ .
COPY etl/ ./etl

EXPOSE 8000
EXPOSE 5678

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# ── Production Target ─────────────────────────────────────────────────────────
FROM base AS production
ENV APP_ENV=production \
    DEBUG=false

# Create a non-root service user for running the application
RUN groupadd -g 1000 appgroup \
    && useradd -u 1000 -g appgroup -m -s /bin/bash appuser

# Copy application source
COPY --chown=appuser:appgroup backend/ $WORKDIR/
COPY --chown=appuser:appgroup etl/ $WORKDIR/etl

# Setup required directories
RUN mkdir -p $WORKDIR/data $WORKDIR/logs \
    && chown -R appuser:appgroup $WORKDIR/data $WORKDIR/logs

USER appuser

EXPOSE 8000

# Health check verifies the API is up and database connection is responsive
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"]
