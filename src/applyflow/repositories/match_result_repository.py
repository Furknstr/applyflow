import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from applyflow.models.match_result import MatchResult


async def create_match_result(
    session: AsyncSession, match_result: MatchResult
) -> MatchResult:
    """Save match result."""
    session.add(match_result)
    await session.commit()
    await session.refresh(match_result)
    return match_result


async def get_match_result_by_job(
    session: AsyncSession, job_id: uuid.UUID
) -> MatchResult | None:
    """Get the latest match result for a specific job."""
    result = await session.execute(
        select(MatchResult)
        .where(MatchResult.job_id == job_id)
        .order_by(MatchResult.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
