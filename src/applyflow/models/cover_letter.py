import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from applyflow.schemas.enums import CoverLetterStatus


class CoverLetter(SQLModel, table=True):
    """Writer Agent'ın ürettiği ön yazı taslağı."""

    __tablename__ = "cover_letters"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_id: uuid.UUID = Field(foreign_key="jobs.id", index=True)
    draft_text: str
    # ChromaDB chunk ID'leri
    used_context_ids: list[str] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    status: CoverLetterStatus = Field(
        default=CoverLetterStatus.DRAFT, max_length=16
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
