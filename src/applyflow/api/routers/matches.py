"""
Matches router — match results.
Matcher Agent will be integrated in Phase 4.
"""

import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from applyflow.db.session import get_session
from applyflow.models.match_result import MatchResult
from applyflow.repositories import get_match_result_by_job

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("/{job_id}", summary="Get match result for job")
async def get_match(
    job_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> MatchResult:
    result = await get_match_result_by_job(session, job_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No match result found for this job",
        )
    return result
