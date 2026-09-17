"""
Cover-letters router — ön yazı taslakları.
Faz 4'te Writer Agent entegre edilecek.
"""

import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from applyflow.db.session import get_session
from applyflow.models.cover_letter import CoverLetter
from applyflow.repositories import (
    get_cover_letter,
    get_cover_letter_by_job,
    update_cover_letter_status,
)
from applyflow.schemas.enums import CoverLetterStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cover-letters", tags=["cover-letters"])


@router.get("/{cover_letter_id}", summary="Ön yazı taslağını getir")
async def get_cover_letter_detail(
    cover_letter_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> CoverLetter:
    cl = await get_cover_letter(session, cover_letter_id)
    if cl is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found",
        )
    return cl


@router.get("/by-job/{job_id}", summary="İlana ait ön yazıyı getir")
async def get_cover_letter_by_job_id(
    job_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> CoverLetter:
    cl = await get_cover_letter_by_job(session, job_id)
    if cl is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cover letter found for this job",
        )
    return cl


@router.patch("/{cover_letter_id}/status", summary="Ön yazı durumunu güncelle")
async def patch_cover_letter_status(
    cover_letter_id: uuid.UUID,
    new_status: CoverLetterStatus,
    session: AsyncSession = Depends(get_session),
) -> CoverLetter:
    cl = await update_cover_letter_status(session, cover_letter_id, new_status)
    if cl is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found",
        )
    return cl
