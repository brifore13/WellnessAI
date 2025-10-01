"""
Client for calling external AI microservice.
This service only handles HTTP communication - AI logic in ai-service
"""
import logging
from typing import Optional, Dict
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """
    HTTP client for Benny AI microservice.

    Responsibility: Call external AI service at port 8001
    """
    def __init__(self) -> None:
        self.base_url = settings.ai_service_url
        self.timeout = 30.0

    async def get_recommendation(
            self,
            nutrition: str,
            sleep: str,
            fitness: str,
            stress: str
    ) -> Optional[str]:
        """
        Call AI microservice for wellness recommendations
        Args:
            Responses to: nutrition, sleep, fitness, stress
        Returns:
            AI reocmmendations string or None if service unavailable
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/recommend",
                    json={
                        "daily_checkin": {
                            "nutrition": nutrition,
                            "sleep": sleep,
                            "fitness": fitness,
                            "stress": stress
                        }
                    },
                    timeout=self.timeout
                )

                response.raise_for_status()
                data = response.json()

                if data.get("success"):
                    return data.get("response")
                else:
                    logger.warning(f"AI service returned success=false: {data.get('error')}")
                    return None

        except httpx.TimeoutError:
            logger.error("AI service timeout")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"AI service HTTP error: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"AI service error: {e}")