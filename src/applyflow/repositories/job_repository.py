import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from applyflow.models.job import Job
from applyflow.models.application_status import ApplicationStatusLog
from applyflow.schemas.enums import ApplicationStatus


async def create_job(session: AsyncSession, job: Job) -> Job:
    """Yeni bir ilanı DB'ye kaydet."""
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


async def get_job(session: AsyncSession, job_id: uuid.UUID) -> Job | None:
    """ID ile ilan getir."""
    result = await session.execute(select(Job).where(Job.id == job_id))
    return result.scalar_one_or_none()


async def get_jobs_by_status(
    session: AsyncSession,
    status: ApplicationStatus,
    limit: int = 100,
    offset: int = 0,
) -> list[Job]:
    """Belirli bir durumdaki ilanları listele."""
    result = await session.execute(
        select(Job).where(Job.status == status).offset(offset).limit(limit)
    )
    return list(result.scalars().all())


async def get_all_jobs(
    session: AsyncSession,
    limit: int = 100,
    offset: int = 0,
) -> list[Job]:
    """Tüm ilanları listele."""
    result = await session.execute(select(Job).offset(offset).limit(limit))
    return list(result.scalars().all())


async def update_job_status(
    session: AsyncSession,
    job_id: uuid.UUID,
    new_status: ApplicationStatus,
    note: str | None = None,
) -> Job | None:
    """İlanın durumunu güncelle ve audit log kaydı oluştur."""
    job = await get_job(session, job_id)
    if job is None:
        return None

    log = ApplicationStatusLog(
        job_id=job_id,
        previous_status=job.status,
        new_status=new_status,
        note=note,
    )
    job.status = new_status
    job.updated_at = datetime.now(UTC)

    session.add(job)
    session.add(log)
    await session.commit()
    await session.refresh(job)
    return job


async def job_exists_by_url(session: AsyncSession, url: str) -> bool:
    """URL'e göre çift kayıt kontrolü."""
    result = await session.execute(select(Job.id).where(Job.url == url))
    return result.first() is not None
