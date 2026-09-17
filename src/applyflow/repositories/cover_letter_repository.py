import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from applyflow.models.cover_letter import CoverLetter
from applyflow.schemas.enums import CoverLetterStatus


async def create_cover_letter(
    session: AsyncSession, cover_letter: CoverLetter
) -> CoverLetter:
    """Ön yazı taslağını kaydet."""
    session.add(cover_letter)
    await session.commit()
    await session.refresh(cover_letter)
    return cover_letter


async def get_cover_letter(
    session: AsyncSession, cover_letter_id: uuid.UUID
) -> CoverLetter | None:
    """ID ile ön yazı getir."""
    result = await session.execute(
        select(CoverLetter).where(CoverLetter.id == cover_letter_id)
    )
    return result.scalar_one_or_none()


async def get_cover_letter_by_job(
    session: AsyncSession, job_id: uuid.UUID
) -> CoverLetter | None:
    """Belirli bir ilanın en son ön yazısını getir."""
    result = await session.execute(
        select(CoverLetter)
        .where(CoverLetter.job_id == job_id)
        .order_by(CoverLetter.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def update_cover_letter_status(
    session: AsyncSession,
    cover_letter_id: uuid.UUID,
    new_status: CoverLetterStatus,
) -> CoverLetter | None:
    """Ön yazının durumunu güncelle."""
    cover_letter = await get_cover_letter(session, cover_letter_id)
    if cover_letter is None:
        return None

    cover_letter.status = new_status
    cover_letter.updated_at = datetime.now(UTC)
    session.add(cover_letter)
    await session.commit()
    await session.refresh(cover_letter)
    return cover_letter
