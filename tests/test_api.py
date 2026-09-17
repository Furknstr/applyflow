"""
FastAPI uygulama testleri — TestClient ile in-process test.

DB bağımlılığı override edilir, gerçek PostgreSQL gerekmez.
"""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

import applyflow.models  # noqa: F401 — SQLModel.metadata kaydı için
from applyflow.api.app import app
from applyflow.db.session import get_session

SQLITE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def client(db_session: AsyncSession) -> TestClient:
    """DB bağımlılığı override edilmiş TestClient."""

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "version" in data


# ---------------------------------------------------------------------------
# Jobs endpoints
# ---------------------------------------------------------------------------


def test_list_jobs_empty(client: TestClient) -> None:
    r = client.get("/jobs/")
    assert r.status_code == 200
    assert r.json() == []


def test_get_job_not_found(client: TestClient) -> None:
    import uuid
    r = client.get(f"/jobs/{uuid.uuid4()}")
    assert r.status_code == 404


def test_patch_job_status_not_found(client: TestClient) -> None:
    import uuid
    r = client.patch(
        f"/jobs/{uuid.uuid4()}/status",
        params={"new_status": "evaluated"},
    )
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Cover-letters endpoints
# ---------------------------------------------------------------------------


def test_get_cover_letter_not_found(client: TestClient) -> None:
    import uuid
    r = client.get(f"/cover-letters/{uuid.uuid4()}")
    assert r.status_code == 404


def test_get_cover_letter_by_job_not_found(client: TestClient) -> None:
    import uuid
    r = client.get(f"/cover-letters/by-job/{uuid.uuid4()}")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Matches endpoints
# ---------------------------------------------------------------------------


def test_get_match_not_found(client: TestClient) -> None:
    import uuid
    r = client.get(f"/matches/{uuid.uuid4()}")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# OpenAPI schema — tüm route'ların kayıtlı olduğunu doğrula
# ---------------------------------------------------------------------------


def test_openapi_paths(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = set(r.json()["paths"].keys())
    expected = {
        "/health",
        "/jobs/",
        "/jobs/{job_id}",
        "/jobs/{job_id}/status",
        "/matches/{job_id}",
        "/cover-letters/{cover_letter_id}",
        "/cover-letters/by-job/{job_id}",
        "/cover-letters/{cover_letter_id}/status",
    }
    assert expected.issubset(paths), f"Missing paths: {expected - paths}"
