"""
Repository for user data access.
"""
from datetime import datetime
import logging
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """Repository for user operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Check if email is already registered."""
        user = await self.get_by_email(email)
        return user is not None

    async def username_exists(self, username: str) -> bool:
        """Check if username is already taken."""
        user = await self.get_by_username(username)
        return user is not None

    async def create_user(
        self,
        email: str,
        username: str,
        hashed_password: str,
        is_demo: bool = False
    ) -> User:
        """Create a new user."""
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_demo=is_demo,
            is_active=True
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"Created user: {email} (demo={is_demo})")
        return user

    async def get_or_create_demo_user(self) -> User:
        """
        Get existing demo user or create one.
        Demo user is shared across all demo sessions.

        Email: demo@bennyai.app
        Username: demo_user
        """
        demo_email = "demo@bennyai.app"
        demo_user = await self.get_by_email(demo_email)

        if demo_user:
            logger.info("Using existing demo user")
            return demo_user

        # Create demo user
        from app.core.auth import get_password_hash

        logger.info("Creating new demo user")
        demo_user = await self.create_user(
            email=demo_email,
            username="demo_user",
            hashed_password=get_password_hash("demo_password_not_used"),
            is_demo=True
        )

        return demo_user

    async def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp."""
        user = await self.get_by_id(user_id)
        if user:
            user.last_login = datetime.now()
            await self.db.commit()