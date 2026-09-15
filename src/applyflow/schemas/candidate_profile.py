import uuid

from pydantic import BaseModel, EmailStr, Field


class CandidateProfile(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    full_name: str
    email: EmailStr
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    skills: list[str] = Field(default_factory=list)
    # IDs of RAG documents (ChromaDB) linked to this profile
    knowledge_doc_ids: list[str] = Field(default_factory=list)
