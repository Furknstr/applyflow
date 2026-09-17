"""
Jobs router — CRUD and status management for job postings.
To be expanded with adapters in Phase 2.
"""

import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from applyflow.db.session import get_session
from applyflow.models.job import Job
from applyflow.repositories import (
    create_job,
    get_job,
    get_all_jobs,
    get_jobs_by_status,
    job_exists_by_url,
    update_job_status,
)
from applyflow.schemas.enums import ApplicationStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", summary="List all jobs")
async def list_jobs(
    status: ApplicationStatus | None = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
) -> list[Job]:
    if status is not None:
        return await get_jobs_by_status(session, status, limit=limit, offset=offset)
    return await get_all_jobs(session, limit=limit, offset=offset)


@router.get("/{job_id}", summary="Get job details")
async def get_job_detail(
    job_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> Job:
    job = await get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.patch("/{job_id}/status", summary="Update job status")
async def patch_job_status(
    job_id: uuid.UUID,
    new_status: ApplicationStatus,
    note: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> Job:
    job = await update_job_status(session, job_id, new_status, note=note)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
