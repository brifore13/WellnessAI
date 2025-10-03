"""
Business logic for chat operations.
"""
import logging
from datetime import date
from typing import List, Dict

from app.repositories.chat import ChatRepository
from app.services.ai import AIService
from app.models.chat import ChatMessage

logger = logging.getLogger(__name__)


class ChatService:
    """
    Service for chat functionality.
    
    Handles:
    - Saving user messages
    - Getting AI responses
    - Retrieving chat history
    """
    
    def __init__(self, chat_repo: ChatRepository, ai_service: AIService):
        self.chat_repo = chat_repo
        self.ai_service = ai_service
    
    async def process_chat_message(
        self,
        user_id: str,
        message: str
    ) -> Dict:
        """
        Process a chat message from user.
        
        Flow:
        1. Get/create today's session
        2. Save user message
        3. Get AI response
        4. Save AI response
        5. Return both messages
        """
        logger.info(f"Processing chat message for user {user_id}")
        
        # Get or create today's session
        today = date.today()
        session = await self.chat_repo.get_or_create_session(user_id, today)
        
        # Get next sequence number
        seq_num = await self.chat_repo.get_next_sequence_number(session.id)
        
        # Save user message
        user_message = await self.chat_repo.save_message(
            session_id=session.id,
            sequence_number=seq_num,
            is_benny=0,
            message_text=message
        )
        
        logger.info(f"Saved user message with sequence {seq_num}")
        
        # Get AI response
        ai_response = await self.ai_service.chat(message)
        
        if ai_response and ai_response.get("success"):
            benny_text = ai_response.get("response", "I'm having trouble right now.")
        else:
            benny_text = "I'm having trouble connecting right now. Please try again."
        
        # Save Benny's response
        benny_message = await self.chat_repo.save_message(
            session_id=session.id,
            sequence_number=seq_num + 1,
            is_benny=1,
            message_text=benny_text
        )
        
        logger.info(f"Saved Benny response with sequence {seq_num + 1}")
        
        return {
            "user_message": user_message.to_dict(),
            "benny_message": benny_message.to_dict()
        }
    
    async def get_chat_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get recent chat messages for user."""
        messages = await self.chat_repo.get_recent_messages(user_id, limit)
        return [msg.to_dict() for msg in messages]