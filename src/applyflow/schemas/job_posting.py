import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field, HttpUrl

from applyflow.schemas.enums import RemoteType


class JobPosting(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    source: str  # e.g. "greenhouse", "lever", "rss", "manual"
    title: str
    company: str
    location: str | None = None
    remote_type: RemoteType = RemoteType.UNKNOWN
    requirements: list[str] = Field(default_factory=list)
    description_raw: str
    url: HttpUrl
    posted_date: datetime | None = None
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
