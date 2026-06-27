# ─────────────────────────────────────────────────────────────────
# Maven AI Service — Dockerfile
# ─────────────────────────────────────────────────────────────────
#
# Uses python:3.11-slim for compatibility and compact size (~120MB).
# Slim is preferred over Alpine for Python projects containing heavy
# data/ML libraries, as Alpine requires compiling C-extensions from scratch,
# leading to extremely slow build times and massive image bloat.
#
# Docker layer caching rules are obeyed: dependencies are copied and installed
# prior to copying the application source.
# ─────────────────────────────────────────────────────────────────

FROM python:3.11-slim

WORKDIR /app

# Copy dependency manifest
COPY requirements.txt .

# Install dependencies without saving pip cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src/

EXPOSE 8000

# Run uvicorn server directly (no shell wrapper)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
