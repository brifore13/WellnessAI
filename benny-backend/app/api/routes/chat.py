"""
Chat API endpoints.
Handles messaging with Benny AI.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.services.chat import ChatService
from app.services.dependencies import get_chat_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


# Schemas
class ChatRequest(BaseModel):
    """Chat message from user."""
    message: str = Field(..., min_length=1, max_length=1000)


class ChatMessageResponse(BaseModel):
    """Single chat message."""
    id: int
    sequence_number: int
    is_benny: int
    message_text: str
    created_at: str


class ChatResponse(BaseModel):
    """Response after sending chat message."""
    success: bool
    user_message: ChatMessageResponse
    benny_message: ChatMessageResponse


class ChatHistoryResponse(BaseModel):
    """Response with chat history."""
    success: bool
    messages: List[ChatMessageResponse]
    count: int


# Endpoints
@router.post("/send", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service)
    # TODO: Add authentication: current_user: dict = Depends(get_current_user)
):
    """
    Send a chat message to Benny.
    
    Flow:
    1. Save user message to database
    2. Get AI response from AI service
    3. Save AI response to database
    4. Return both messages
    """
    # TODO: Get user_id from authentication
    user_id = "demo_user"
    
    try:
        result = await service.process_chat_message(
            user_id=user_id,
            message=request.message
        )
        
        logger.info(f"Chat message processed for user {user_id}")
        
        return ChatResponse(
            success=True,
            user_message=ChatMessageResponse(**result["user_message"]),
            benny_message=ChatMessageResponse(**result["benny_message"])
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = 20,
    service: ChatService = Depends(get_chat_service)
    # TODO: Add authentication: current_user: dict = Depends(get_current_user)
):
    """
    Get user's recent chat history.
    
    Returns up to 'limit' most recent messages across all sessions.
    """
    # TODO: Get user_id from authentication
    user_id = "demo_user"
    
    try:
        messages = await service.get_chat_history(user_id, limit)
        
        chat_messages = [ChatMessageResponse(**msg) for msg in messages]
        
        return ChatHistoryResponse(
            success=True,
            messages=chat_messages,
            count=len(chat_messages)
        )
        
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch chat history"
        )