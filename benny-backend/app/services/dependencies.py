"""
FastAPI dependency injection for services.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.repositories.user import UserRepository
from app.services.auth import AuthService

from app.core.database import get_database
from app.repositories.checkin import CheckinRepository
from app.services.checkin import CheckinService
from app.services.ai import AIService

security = HTTPBearer()


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


def get_user_repository(
    db: AsyncSession = Depends(get_database)
) -> UserRepository:
    """Provide UserRepository."""
    return UserRepository(db)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthService:
    """Provide AuthService."""
    return AuthService(user_repo)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Dependency to get current authenticated user from token.
    Use this in protected routes.
    """
    token = credentials.credentials
    user = await auth_service.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_id(
    user=Depends(get_current_user)
) -> str:
    """Get just the user ID from current user."""
    return str(user.id)
