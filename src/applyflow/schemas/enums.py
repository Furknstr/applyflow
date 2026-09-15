from enum import StrEnum


class ApplicationStatus(StrEnum):
    DISCOVERED = "discovered"
    EVALUATED = "evaluated"
    DRAFTED = "drafted"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    REJECTED = "rejected"
    SKIPPED = "skipped"
    ERROR = "error"


class CoverLetterStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"


class RemoteType(StrEnum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    UNKNOWN = "unknown"
