"""
Candidates router — candidate profile management.
To be expanded with RAG integration in Phase 3.
"""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/candidates", tags=["candidates"])

# In Phase 3, CandidateProfile model will be moved to DB and
# CRUD endpoints will be added here.
