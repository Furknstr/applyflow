# Application-wide constants
# Add typed constants here instead of magic numbers/strings scattered in code.

DEFAULT_MATCH_SCORE_THRESHOLD: float = 0.7
RAG_TOP_K_CHUNKS: int = 5
RAG_CHUNK_SIZE: int = 400  # tokens
RAG_CHUNK_OVERLAP: int = 50  # tokens

APPLICATION_STATUSES = [
    "discovered",
    "evaluated",
    "drafted",
    "pending_approval",
    "approved",
    "submitted",
    "rejected",
    "skipped",
    "error",
]
