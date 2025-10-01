"""
FastAPI dependency injection for services.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_database
from app.repositories.checkin import CheckinRepository
from app.services.checkin import CheckinService
from app.services.ai import AIService


def get_checkin_repository(
    db: AsyncSession = Depends(get_database)
) -> CheckinRepository:
    """Provide CheckinRepository."""
    return CheckinRepository(db)


def get_ai_service() -> AIService:
    """Provide AIService."""
    return AIService()


def get_checkin_service(
    checkin_repo: CheckinRepository = Depends(get_checkin_repository),
    ai_service: AIService = Depends(get_ai_service)
) -> CheckinService:
    """Provide CheckinService."""
    return CheckinService(checkin_repo, ai_service)