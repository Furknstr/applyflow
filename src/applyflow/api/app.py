"""
Ana FastAPI uygulama modülü.

Başlatma sırası:
  1. Lifespan context — DB engine kontrolü
  2. Middleware — CORS, logging
  3. Router kayıtları
"""

import logging
import time
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from applyflow.core.config import settings
from applyflow.api.routers import (
    jobs_router,
    candidates_router,
    matches_router,
    cover_letters_router,
)

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Uygulama başlangıç / bitiş kancaları."""
    logger.info("ApplyFlow starting up…")
    yield
    logger.info("ApplyFlow shutting down…")


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="Autonomous multi-agent job application assistant",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next: object) -> Response:
    """Her isteği latency ile logla."""
    start = time.perf_counter()
    response: Response = await call_next(request)  # type: ignore[operator]
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s → %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["system"], summary="Servis sağlık kontrolü")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": settings.app_version}


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(jobs_router)
app.include_router(candidates_router)
app.include_router(matches_router)
app.include_router(cover_letters_router)
