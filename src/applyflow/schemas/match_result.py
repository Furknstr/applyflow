import uuid

from pydantic import BaseModel, Field, field_validator

from applyflow.core.constants import DEFAULT_MATCH_SCORE_THRESHOLD


class MatchResult(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    job_id: uuid.UUID
    score: float = Field(ge=0.0, le=1.0)
    matched_keywords: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    agent_notes: str | None = None

    @field_validator("score")
    @classmethod
    def round_score(cls, v: float) -> float:
        return round(v, 4)

    @property
    def is_above_threshold(self) -> bool:
        return self.score >= DEFAULT_MATCH_SCORE_THRESHOLD
