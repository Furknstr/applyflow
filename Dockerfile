# syntax=docker/dockerfile:1
# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — Build: bağımlılıkları kur
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.13-slim AS builder

# uv — hızlı Python paket yöneticisi
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Sadece dependency dosyalarını kopyala (layer cache için)
COPY pyproject.toml uv.lock README.md ./

# Bağımlılıkları sanal ortama kur (dev hariç)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — Runtime: minimal çalışma imajı
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.13-slim AS runtime

# Güvenlik: root olmayan kullanıcı
RUN groupadd --system applyflow && \
    useradd --system --gid applyflow --home /app --shell /sbin/nologin applyflow

WORKDIR /app

# Build stage'den sanal ortamı kopyala
COPY --from=builder /app/.venv /app/.venv

# Uygulama kaynak kodunu kopyala
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY main.py ./

# PATH'e venv'i ekle
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Kullanıcıya geç
USER applyflow

EXPOSE 8000

# Başlangıç: migration çalıştır, ardından sunucuyu başlat
CMD ["sh", "-c", "python -m alembic upgrade head && uvicorn applyflow.api.app:app --host 0.0.0.0 --port 8000 --workers 1"]
