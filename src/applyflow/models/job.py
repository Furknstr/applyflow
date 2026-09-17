import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Column, String
from sqlmodel import Field, SQLModel

from applyflow.schemas.enums import ApplicationStatus, RemoteType


class Job(SQLModel, table=True):
    """Persisted job posting record."""

    __tablename__ = "jobs"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )
    source: str = Field(max_length=64)
    title: str = Field(max_length=256)
    company: str = Field(max_length=256)
    location: str | None = Field(default=None, max_length=256)
    remote_type: RemoteType = Field(default=RemoteType.UNKNOWN, max_length=16)
    # Stored as JSON array in DB
    requirements: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    description_raw: str
    url: str = Field(max_length=2048)
    status: ApplicationStatus = Field(
        default=ApplicationStatus.DISCOVERED, max_length=32
    )
    posted_date: datetime | None = None
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
