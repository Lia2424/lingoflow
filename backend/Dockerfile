FROM python:3.11-slim AS base

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Install dependencies separately from source for better layer caching
COPY pyproject.toml .
RUN uv pip install --system -e "."

# ── Development target ────────────────────────────────────────────────────────
FROM base AS dev
RUN uv pip install --system -e ".[dev]"
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ── Production target ─────────────────────────────────────────────────────────
FROM base AS prod
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
