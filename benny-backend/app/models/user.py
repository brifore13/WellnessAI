"""
User model for authentication.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.core.database import Base


class User(Base):
    """User account for authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_demo = Column(Boolean, default=False)  # Flag for demo accounts
    created_at = Column(DateTime(timezone=False), nullable=False, default=datetime.now)
    last_login = Column(DateTime(timezone=False), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, is_demo={self.is_demo})>"

    def to_dict(self):
        """Convert to dictionary for API responses (excludes password)."""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "is_demo": self.is_demo,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
