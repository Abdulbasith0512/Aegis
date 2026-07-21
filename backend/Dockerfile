# Slim production image for AegisAI FastAPI Backend Gateway
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir --default-timeout=100 --user -r backend/requirements.txt

FROM python:3.12-slim AS runner

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy backend app and structural ML/agents dependencies
COPY backend ./backend
COPY agents ./agents
COPY ml ./ml

# Expose API gateway port
EXPOSE 8000

# Set Python search paths
ENV PYTHONPATH=/app

WORKDIR /app/backend

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
