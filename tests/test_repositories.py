"""
DB layer tests — uses SQLite in-memory DB (does not require PostgreSQL).

An isolated DB and session is created for each test.
"""

import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

# Import models — so they get registered to SQLModel.metadata
import applyflow.models  # noqa: F401

from applyflow.models.job import Job
from applyflow.models.match_result import MatchResult
from applyflow.models.cover_letter import CoverLetter
from applyflow.repositories.job_repository import (
    create_job,
    get_job,
    get_all_jobs,
    get_jobs_by_status,
    job_exists_by_url,
    update_job_status,
)
from applyflow.repositories.match_result_repository import (
    create_match_result,
    get_match_result_by_job,
)
from applyflow.repositories.cover_letter_repository import (
    create_cover_letter,
    get_cover_letter,
    get_cover_letter_by_job,
    update_cover_letter_status,
)
from applyflow.schemas.enums import ApplicationStatus, CoverLetterStatus

SQLITE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    """A clean in-memory SQLite session for each test."""
    engine = create_async_engine(SQLITE_URL, connect_args={"check_same_thread": False})

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as s:
        yield s

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


def make_job(**kwargs: object) -> Job:
    defaults = {
        "source": "greenhouse",
        "title": "Backend Engineer",
        "company": "Acme Corp",
        "description_raw": "We are looking for a backend engineer.",
        "url": f"https://example.com/jobs/{uuid.uuid4()}",
    }
    defaults.update(kwargs)
    return Job(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Job repository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_and_get_job(session: AsyncSession) -> None:
    job = make_job()
    created = await create_job(session, job)

    assert created.id == job.id
    fetched = await get_job(session, job.id)
    assert fetched is not None
    assert fetched.title == "Backend Engineer"


@pytest.mark.asyncio
async def test_get_job_not_found(session: AsyncSession) -> None:
    result = await get_job(session, uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_get_all_jobs(session: AsyncSession) -> None:
    await create_job(session, make_job(title="Job A"))
    await create_job(session, make_job(title="Job B"))

    all_jobs = await get_all_jobs(session)
    assert len(all_jobs) == 2


@pytest.mark.asyncio
async def test_get_jobs_by_status(session: AsyncSession) -> None:
    await create_job(session, make_job(title="Discovered Job"))
    job2 = make_job(title="Evaluated Job", status=ApplicationStatus.EVALUATED)
    await create_job(session, job2)

    discovered = await get_jobs_by_status(session, ApplicationStatus.DISCOVERED)
    assert len(discovered) == 1
    assert discovered[0].title == "Discovered Job"


@pytest.mark.asyncio
async def test_update_job_status(session: AsyncSession) -> None:
    job = await create_job(session, make_job())
    updated = await update_job_status(
        session, job.id, ApplicationStatus.EVALUATED, note="Matcher passed"
    )

    assert updated is not None
    assert updated.status == ApplicationStatus.EVALUATED


@pytest.mark.asyncio
async def test_update_job_status_not_found(session: AsyncSession) -> None:
    result = await update_job_status(session, uuid.uuid4(), ApplicationStatus.EVALUATED)
    assert result is None


@pytest.mark.asyncio
async def test_job_exists_by_url(session: AsyncSession) -> None:
    url = "https://example.com/jobs/unique-123"
    job = make_job(url=url)
    await create_job(session, job)

    assert await job_exists_by_url(session, url) is True
    assert await job_exists_by_url(session, "https://example.com/jobs/other") is False


# ---------------------------------------------------------------------------
# MatchResult repository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_and_get_match_result(session: AsyncSession) -> None:
    job = await create_job(session, make_job())

    mr = MatchResult(
        job_id=job.id,
        score=0.85,
        matched_keywords=["python", "fastapi"],
        gaps=["kubernetes"],
        agent_notes="Good fit overall.",
    )
    created = await create_match_result(session, mr)
    assert created.id == mr.id

    fetched = await get_match_result_by_job(session, job.id)
    assert fetched is not None
    assert fetched.score == 0.85


@pytest.mark.asyncio
async def test_get_match_result_not_found(session: AsyncSession) -> None:
    result = await get_match_result_by_job(session, uuid.uuid4())
    assert result is None


# ---------------------------------------------------------------------------
# CoverLetter repository
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_and_get_cover_letter(session: AsyncSession) -> None:
    job = await create_job(session, make_job())

    cl = CoverLetter(
        job_id=job.id,
        draft_text="Dear Hiring Manager, ...",
        used_context_ids=["chunk-1", "chunk-2"],
    )
    created = await create_cover_letter(session, cl)
    assert created.id == cl.id

    fetched = await get_cover_letter(session, cl.id)
    assert fetched is not None
    assert fetched.draft_text == "Dear Hiring Manager, ..."


@pytest.mark.asyncio
async def test_get_cover_letter_by_job(session: AsyncSession) -> None:
    job = await create_job(session, make_job())
    cl = CoverLetter(job_id=job.id, draft_text="Hello!")
    await create_cover_letter(session, cl)

    fetched = await get_cover_letter_by_job(session, job.id)
    assert fetched is not None
    assert fetched.job_id == job.id


@pytest.mark.asyncio
async def test_update_cover_letter_status(session: AsyncSession) -> None:
    job = await create_job(session, make_job())
    cl = CoverLetter(job_id=job.id, draft_text="Draft text.")
    created = await create_cover_letter(session, cl)

    updated = await update_cover_letter_status(
        session, created.id, CoverLetterStatus.APPROVED
    )
    assert updated is not None
    assert updated.status == CoverLetterStatus.APPROVED
