"""
Benny AI - Core wellness coach implementation
"""
import logging
from datetime import datetime
from typing import Dict
from enum import Enum

from openai import AzureOpenAI

from src.core.config import settings

logger = logging.getLogger(__name__)


class BennyMode(str, Enum):
    """Different response styles for Benny"""
    CHAT = "chat"
    RECOMMEND = "recommend"


class BennyWellnessAI:
    """
    Benny AI - Wellness coaching with Azure OpenAI.
    Responsibilities:
        - Generate AI responses for chat and recommendations
        - Manage conversation context
        - Format prompts for different modes
    """

    BASE_PERSONALITY = """ You are Benny, you a warm and
    motivational wellness coach who uses evidence-based
    research with psychology to provide education, motivation
    and encouragement. You have a strong knowledge of nutrition,
    exercise science, physiology, kinesiology, sleep science,
    behavioral psychology, and psychological wellness. You
    do not provide medical advice. """

    MODE_CONFIG = {
        BennyMode.CHAT: {
            "prompt": """
            - Respond to their question, comment, or insight with curiosity,
            - motivation, or understanding
            - Provide 1 actionable recommendation
            - Give 1-2 reasons why this action works (research based, but simple)
            - Keep responses to 150 words
            - Ask one thoughtful follow-up question
            - If user wants suggestions, give 1 or 2 max to keep chat shorter
            """,
            "max_tokens": 150,
            "temperature": 0.6
        },
        BennyMode.RECOMMEND: {
            "prompt": """
            - Analyze the daily check-in data (nutrition, fitness, stress, sleep)
            - Identify the area that needs the most improvement
            - Give exactly one sentence of actionable advice
            - include specific numbers, times, or techniques
            """,
            "max_tokens": 50,
            "temperature": 0.4,
        }
    }

    def __init__(self):
        """Initialize Benny with Azure OpenAI client"""
        # Validate configuration
        if not settings.azure_openai_endpoint or not settings.azure_openai_api_key:
            raise ValueError("Missing Azure OpenAI credentials in environment")
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version
        )

        self.deployment = settings.azure_openai_deployment
        self.conversation_history = []

        logger.info("Benny AI initialized successfully")

    async def chat(self, message: str) -> Dict: 
        """
        Chat with Benny
        Args:
            message: User's message

        Returns:
            Response dictionary with success, response, tokens_used
        """
        return await self._generate_response(
            message=message,
            mode=BennyMode.CHAT
        )

    async def recommend(self, daily_checkin: Dict) -> Dict:
        """
        Get wellness recommendation based on daily check-in data.
        Args:
            daily_checkin: Dict with nutrition, fitness, stress, sleep

        Returns:
            Response dictionary success, response, tokens_used
        """
        checkin_message = self._format_checkin(daily_checkin)

        benny_prompt = f"""
        Here is today's check in data:
        {checkin_message}

        Do not repeat the checkin data to the user. Respond with one simple,
        actionable goal that will make the biggest positive impact based on
        their response. If all areas are good, give one actionable goal to
        improve. Keep the suggestion short, to one sentence and remain positive.
        """

        return await self._generate_response(
            message=benny_prompt,
            mode=BennyMode.RECOMMEND
        )

    def _format_checkin(self, daily_checkin: Dict) -> str:
        """Format daily checkin-data to send to ai"""
        parts = []

        if "nutrition" in daily_checkin:
            parts.append(f"Today my nutrition was {daily_checkin['nutrition']}.")
        if "fitness" in daily_checkin:
            parts.append(f"Was I able to complete my planned fitness: {daily_checkin['fitness']}.")
        if "stress" in daily_checkin:
            parts.append(f"My stress was {daily_checkin['stress']}.")
        if "sleep" in daily_checkin:
            parts.append(f"My sleep quality was {daily_checkin['sleep']}.")
        
        return " ".join(parts)

    async def _generate_response(self, message: str, mode: BennyMode) -> Dict:
        """
        Generate AI response using Azure Open AI
        Args:
            message: User input or formatted prompt
            mode: Response mode (CHAT or RECOMMEND)
        Returns:
            Response dict
        """

        try:
            # get the system prompt for this mode
            config = self.MODE_CONFIG[mode]
            system_prompt = self.BASE_PERSONALITY + config["prompt"]

            # Build messages for API call
            messages = [{"role": "system", "content": system_prompt}]

            # add convo history for chat mode (10 tokens)
            if mode == BennyMode.CHAT and self.conversation_history:
                messages.extend(self.conversation_history[-10:])
            
            messages.append({"role": "user", "content": message})
            
            # Call Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_tokens=config["max_tokens"],
                temperature=config["temperature"],
                top_p=0.9,
                frequency_penalty=0.3,
                presence_penalty=0.2
            )
            
            benny_response = response.choices[0].message.content.strip()
            
            # Update conversation history
            if mode == BennyMode.CHAT:
                self.conversation_history.extend([
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": benny_response}
                ])
            
            return {
                "success": True,
                "response": benny_response,
                "mode": mode.value,
                "tokens_used": response.usage.total_tokens,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "success": False,
                "error": str(e),
                "mode": mode.value,
                "response": self._get_fallback_response(mode),
                "timestamp": datetime.now().isoformat()
            }

    def _get_fallback_response(self, mode: BennyMode) -> str:
        """Get fallback repsonse when AI fails"""
        fallbacks = {
            BennyMode.CHAT: """Benny: Taking a quick break, please try again later.""",
            BennyMode.RECOMMEND: """Take a deep breath and try a 5-minute walk outside."""
        }
        return fallbacks[mode]

    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
        return {"success": True, "message": "Conversation history cleared"}
    