import uuid
from datetime import datetime

import pytest

from applyflow.schemas import (
    ApplicationStatus,
    CandidateProfile,
    CoverLetterDraft,
    CoverLetterStatus,
    JobPosting,
    MatchResult,
    RemoteType,
)


class TestApplicationStatus:
    def test_all_statuses_exist(self) -> None:
        statuses = [s.value for s in ApplicationStatus]
        assert "discovered" in statuses
        assert "evaluated" in statuses
        assert "drafted" in statuses
        assert "pending_approval" in statuses
        assert "approved" in statuses
        assert "submitted" in statuses
        assert "rejected" in statuses
        assert "skipped" in statuses
        assert "error" in statuses


class TestJobPosting:
    def test_default_id_generated(self) -> None:
        job = JobPosting(
            source="greenhouse",
            title="Backend Engineer",
            company="Acme",
            description_raw="We need a backend engineer.",
            url="https://example.com/jobs/1",
        )
        assert isinstance(job.id, uuid.UUID)

    def test_default_remote_type(self) -> None:
        job = JobPosting(
            source="lever",
            title="ML Engineer",
            company="Tech Co",
            description_raw="...",
            url="https://example.com/jobs/2",
        )
        assert job.remote_type == RemoteType.UNKNOWN

    def test_requirements_default_empty(self) -> None:
        job = JobPosting(
            source="manual",
            title="Intern",
            company="Startup",
            description_raw="...",
            url="https://example.com/jobs/3",
        )
        assert job.requirements == []

    def test_scraped_at_auto_set(self) -> None:
        job = JobPosting(
            source="rss",
            title="DevOps",
            company="Corp",
            description_raw="...",
            url="https://example.com/jobs/4",
        )
        assert isinstance(job.scraped_at, datetime)


class TestCandidateProfile:
    def test_basic_creation(self) -> None:
        profile = CandidateProfile(
            full_name="Furkan Test",
            email="furkan@example.com",
            skills=["Python", "FastAPI"],
        )
        assert profile.full_name == "Furkan Test"
        assert "Python" in profile.skills

    def test_optional_fields_default_none(self) -> None:
        profile = CandidateProfile(full_name="Test", email="t@example.com")
        assert profile.phone is None
        assert profile.linkedin_url is None


class TestMatchResult:
    def test_score_rounded(self) -> None:
        result = MatchResult(job_id=uuid.uuid4(), score=0.123456789)
        assert result.score == 0.1235

    def test_above_threshold(self) -> None:
        result = MatchResult(job_id=uuid.uuid4(), score=0.8)
        assert result.is_above_threshold is True

    def test_below_threshold(self) -> None:
        result = MatchResult(job_id=uuid.uuid4(), score=0.5)
        assert result.is_above_threshold is False

    def test_score_bounds(self) -> None:
        with pytest.raises(Exception):
            MatchResult(job_id=uuid.uuid4(), score=1.5)


class TestCoverLetterDraft:
    def test_default_status_is_draft(self) -> None:
        draft = CoverLetterDraft(job_id=uuid.uuid4(), draft_text="Dear Hiring Manager...")
        assert draft.status == CoverLetterStatus.DRAFT

    def test_context_ids_default_empty(self) -> None:
        draft = CoverLetterDraft(job_id=uuid.uuid4(), draft_text="...")
        assert draft.used_context_ids == []
