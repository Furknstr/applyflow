import uuid
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel

from applyflow.schemas.enums import ApplicationStatus


class ApplicationStatusLog(SQLModel, table=True):
    """Bir ilanın durum değişiklik geçmişi (audit trail)."""

    __tablename__ = "application_status_logs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_id: uuid.UUID = Field(foreign_key="jobs.id", index=True)
    previous_status: ApplicationStatus | None = Field(default=None, max_length=32)
    new_status: ApplicationStatus = Field(max_length=32)
    note: str | None = None
    changed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
