"""
Business logic for daily check-in operations
"""
import logging
from typing import Optional, List
from datetime import date

from app.repositories.checkin import CheckinRepository
from app.services.ai import AIService
from app.models.checkin import (
    DailyCheckin,
    NutritionRating,
    SleepRating,
    FitnessCompletion,
    StressLevel
)

logger = logging.getLogger(__name__)


class DuplicateCheckinError(Exception):
    """Raised when user tries to submit multiple check-ins in one day."""
    pass


class CheckinService:
    """
    Business logic for check-ins.
    Rules:
    - One check-in per user per day
    - AI recommendation is optional (check-in succeeds even if AI fails)
    """
    def __init__(self, checkin_repo: CheckinRepository, ai_service: AIService):
        self.checkin_repo = checkin_repo
        self.ai_service = ai_service

    async def submit_checkin(
        self,
        user_id: str,
        nutrition: str,
        sleep_quality: str,
        fitness: str,
        stress_level: str
    ) -> DailyCheckin:
        """
        Process daily check-in submission.
        Args:
            user_id, nutition, sleep_quality, fitness, stress_level
        Returns:
            DailyCheckin with option AI recommendation
        Raises:
            DuplicateCheckinError: if user already checked in today
            ValueError: If button response is invalid
        """
        logger.info(f"Processing check-in for user {user_id}")

        # Business Rule: One check in a day
        if await self.checkin_repo.has_checkin_today(user_id):
            raise DuplicateCheckinError(
                "You've already completed your check-in today."
            )

        # Convert strings to enums
        try:
            nutrition_enum = NutritionRating(nutrition)
            sleep_enum = SleepRating(sleep_quality)
            fitness_enum = FitnessCompletion(fitness)
            stress_enum = StressLevel(stress_level)
        except ValueError as e:
            logger.error(f"Invalid check-in value: {e}")
            raise ValueError(f"Invalid check-in repsonse: {e}")
        
        # Save check-in (without AI rec yet)
        checkin = await self.checkin_repo.create_checkin(
            user_id=user_id,
            nutrition=nutrition_enum,
            sleep_quality=sleep_enum,
            fitness=fitness_enum,
            stress_level=stress_enum
        )

        logger.info(f"Check-in saved with ID {checkin.id}")

        # Try to get AI recommendation
        recommendation = await self.ai_service.get_recommendation(
            nutrition=nutrition,
            sleep=sleep_quality,
            fitness=fitness,
            stress=stress_level
        )

        if recommendation:
            checkin.ai_recommendation = recommendation
            logger.info("Added AI recommendation")
        else:
            logger.warning("No AI recommendation received")

        return checkin
    
    async def get_user_history(
            self,
            user_id: str,
            limit: int = 30
    ) -> List[DailyCheckin]:
        """Get user's check-in history."""
        return await self.checkin_repo.get_user_checkins(user_id, limit=limit)
    
    async def get_user_streak(self, user_id: str) -> int:
        """Get consecutive check-in days."""
        return await self.checkin_repo.get_checkin_streak(user_id)