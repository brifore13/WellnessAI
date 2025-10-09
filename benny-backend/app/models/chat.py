"""
Database models for chat conversations.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class ChatSession(Base):
    """
    Chat session - groups messages by date.
    One session per user per day.
    """
    
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    session_date = Column(DateTime(timezone=False), nullable=False, index=True)
    created_at = Column(DateTime(timezone=False), nullable=False, default=datetime.now)
    
    # Relationship to messages
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatSession(id={self.id}, user_id={self.user_id}, date={self.session_date})>"


class ChatMessage(Base):
    """
    Individual chat message.
    0 = user message, 1 = Benny message.
    """
    
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    sequence_number = Column(Integer, nullable=False)
    is_benny = Column(Integer, nullable=False)  # 0=user, 1=benny
    message_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=False), nullable=False, default=datetime.now)
    
    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        sender = "Benny" if self.is_benny else "User"
        return f"<ChatMessage(id={self.id}, sender={sender}, seq={self.sequence_number})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "sequence_number": self.sequence_number,
            "is_benny": self.is_benny,
            "message_text": self.message_text,
            "created_at": self.created_at.isoformat()
        }