"""
Authentication service.
Handles user registration, login, and token management.
"""
import logging
from typing import Optional, Dict
from datetime import datetime

from app.repositories.user import UserRepository
from app.core.auth import (
    verify_password,
    get_password_hash,
    create_access_token
)
from app.models.user import User

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class AuthService:
    """Service for authentication operations."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(
        self,
        email: str,
        username: str,
        password: str
    ) -> Dict:
        """
        Register a new user.

        Returns:
            Dict with user info and access token

        Raises:
            AuthenticationError: If email/username already exists
        """
        # Check if email exists
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise AuthenticationError("Email already registered")

        # Check if username exists
        existing_user = await self.user_repo.get_by_username(username)
        if existing_user:
            raise AuthenticationError("Username already taken")

        # Create user
        hashed_password = get_password_hash(password)
        user = await self.user_repo.create_user(
            email=email,
            username=username,
            hashed_password=hashed_password
        )

        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})

        logger.info(f"New user registered: {email}")

        return {
            "user": user.to_dict(),
            "access_token": access_token,
            "token_type": "bearer"
        }

    async def login(self, email: str, password: str) -> Dict:
        """
        Authenticate user and return token.

        Returns:
            Dict with user info and access token

        Raises:
            AuthenticationError: If credentials invalid
        """
        # Get user
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise AuthenticationError("Invalid email or password")

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        # Check if active
        if not user.is_active:
            raise AuthenticationError("Account is inactive")

        # Update last login
        user.last_login = datetime.now()
        await self.user_repo.db.commit()

        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})

        logger.info(f"User logged in: {email}")

        return {
            "user": user.to_dict(),
            "access_token": access_token,
            "token_type": "bearer"
        }

    async def demo_login(self) -> Dict:
        """
        Create or get demo user session.
        No password required - instant access.
        """
        # Get or create demo user
        demo_user = await self.user_repo.get_or_create_demo_user()

        # Create token
        access_token = create_access_token(data={"sub": str(demo_user.id)})

        logger.info("Demo user session created")

        return {
            "user": demo_user.to_dict(),
            "access_token": access_token,
            "token_type": "bearer",
            "is_demo": True
        }

    async def get_current_user(self, token: str) -> Optional[User]:
        """
        Get user from JWT token.

        Args:
            token: JWT access token

        Returns:
            User object or None if invalid
        """
        from app.core.auth import decode_access_token

        payload = decode_access_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        try:
            user = await self.user_repo.get_by_id(int(user_id))
            return user
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None