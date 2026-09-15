import uuid

from pydantic import BaseModel, Field

from applyflow.schemas.enums import CoverLetterStatus


class CoverLetterDraft(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    job_id: uuid.UUID
    draft_text: str
    # ChromaDB chunk IDs used to generate this draft
    used_context_ids: list[str] = Field(default_factory=list)
    status: CoverLetterStatus = CoverLetterStatus.DRAFT
