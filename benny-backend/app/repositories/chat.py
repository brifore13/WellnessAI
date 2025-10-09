"""
Repository for chat data access.
"""
from datetime import datetime, date
from typing import List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatSession, ChatMessage
from app.repositories.base import BaseRepository


class ChatRepository(BaseRepository[ChatMessage]):
    """Repository for chat operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(ChatMessage, db)
    
    async def get_or_create_session(self, user_id: str, session_date: date) -> ChatSession:
        """
        Get existing session or create new one for user/date.
        """
        # Try to find existing session
        result = await self.db.execute(
            select(ChatSession)
            .where(
                and_(
                    ChatSession.user_id == user_id,
                    ChatSession.session_date == session_date
                )
            )
        )
        session = result.scalar_one_or_none()
        
        if session:
            return session
        
        # Create new session
        session = ChatSession(
            user_id=user_id,
            session_date=datetime.combine(session_date, datetime.min.time())
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session
    
    async def save_message(
        self,
        session_id: int,
        sequence_number: int,
        is_benny: int,
        message_text: str
    ) -> ChatMessage:
        """Save a chat message."""
        message = ChatMessage(
            session_id=session_id,
            sequence_number=sequence_number,
            is_benny=is_benny,
            message_text=message_text
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
    
    async def get_session_messages(self, session_id: int) -> List[ChatMessage]:
        """Get all messages for a session, ordered by sequence."""
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.sequence_number)
        )
        return list(result.scalars().all())
    
    async def get_recent_messages(self, user_id: str, limit: int = 20) -> List[ChatMessage]:
        """
        Get recent messages across all sessions for user.
        """
        # Get recent sessions
        sessions_result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.session_date.desc())
            .limit(5)  # Last 5 days
        )
        sessions = sessions_result.scalars().all()
        
        if not sessions:
            return []
        
        session_ids = [s.id for s in sessions]
        
        # Get messages from those sessions
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id.in_(session_ids))
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        messages.reverse()  # Chronological order
        return messages
    
    async def get_next_sequence_number(self, session_id: int) -> int:
        """Get next sequence number for session."""
        result = await self.db.execute(
            select(ChatMessage.sequence_number)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.sequence_number.desc())
            .limit(1)
        )
        last_seq = result.scalar_one_or_none()
        return (last_seq + 1) if last_seq else 1
