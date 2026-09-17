import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class MatchResult(SQLModel, table=True):
    """Matcher Agent çıktısı — bir ilan için eşleşme sonucu."""

    __tablename__ = "match_results"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_id: uuid.UUID = Field(foreign_key="jobs.id", index=True)
    score: float = Field(ge=0.0, le=1.0)
    matched_keywords: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    gaps: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    agent_notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
