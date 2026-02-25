# ── Stage 1: Build dependencies in a venv ──────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install only the Python deps into a virtual-env so we can
# copy the whole venv to the final image (keeps it small).
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ── Stage 2: Runtime image ─────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Bring the pre-built venv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source code
COPY config/  config/
COPY ingestion/ ingestion/
COPY llm/     llm/
COPY process/ process/
COPY src/     src/
COPY vector_db/ vector_db/
COPY data/    data/

# Flask listens on port 5000
EXPOSE 5000

# Run with Flask's built‑in server (use gunicorn for production)
CMD ["python", "src/main.py"]
