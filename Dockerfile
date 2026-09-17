# syntax=docker/dockerfile:1
# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — Build: install dependencies
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.13-slim AS builder

# uv — fast Python package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy only dependency files (for layer cache)
COPY pyproject.toml uv.lock README.md ./

# Install dependencies to virtual environment (excluding dev)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — Runtime: minimal runtime image
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.13-slim AS runtime

# Security: non-root user
RUN groupadd --system applyflow && \
    useradd --system --gid applyflow --home /app --shell /sbin/nologin applyflow

WORKDIR /app

# Copy virtual environment from build stage
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY main.py ./

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Switch to user
USER applyflow

EXPOSE 8000

# Entrypoint: run migration, then start server
CMD ["sh", "-c", "python -m alembic upgrade head && uvicorn applyflow.api.app:app --host 0.0.0.0 --port 8000 --workers 1"]
