"""
Candidates router — aday profili yönetimi.
Faz 3'te RAG entegrasyonu ile genişletilecek.
"""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/candidates", tags=["candidates"])

# Faz 3'te CandidateProfile modeli DB'ye taşınacak ve
# CRUD endpoint'leri buraya eklenecek.
