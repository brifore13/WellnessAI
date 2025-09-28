"""
FastAPI dependencies for dependency injection.
Provides clean separation of concerns and easy testing.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_database
from app.repositories.checkin import CheckinRepository
from app.repositories.chat import ChatRepository
from app.services.checkin import CheckinService
from app.services.chat import ChatService
from app.services.ai import AIService


# Repository Dependencies
def get_checkin_repository(
        db: AsyncSession = Depends(get_database)
) -> CheckinRepository:
    """Provide Checkin Repository instance."""
    return CheckinRepository(db)


def get_chat_repository(
        db: AsyncSession = Depends(get_database)
) -> ChatRepository:
    """Provide ChatRepository instance."""
    return ChatRepository(db)


# Service Dependencies
def get_ai_service() -> AIService:
    """Provide AIService instance."""
    return AIService()


def get_checkin_service(
        checkin_repo: CheckinRepository = Depends(get_checkin_repository),
        ai_service: AIService = Depends(get_ai_service)
) -> CheckinService:
    """Provide CheckinService instance."""
    return CheckinService(checkin_repo, ai_service)


def get_chat_service(
        chat_repo: ChatRepository = Depends(get_chat_repository),
        ai_service: AIService = Depends(get_ai_service)
) -> ChatService:
    """Provide ChatService instance."""
    return ChatService(chat_repo, ai_service)

