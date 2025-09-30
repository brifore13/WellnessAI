"""
Repository for daily check-in data access.
Handles button-based check-in responses.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checkin import (
    DailyCheckin,
    NutritionRating,
    SleepRating,
    FitnessCompletion,
    StressLevel
)
from app.repositories.base import BaseRepository


class checkinRepository(BaseRepository[DailyCheckin]):
    """Repository for daily check-in operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(DailyCheckin, db)

    async def create_checkin(
            self,
            user_id: str,
            nutrition: NutritionRating,
            sleep_quality: SleepRating,
            fitness: FitnessCompletion,
            stress_level: StressLevel,
            ai_recommendation: Optional[str] = None
    ) -> DailyCheckin:
        """Create a new daily check-in with button responses."""
        return await self.create(
            user_id=user_id,
            log_date=datetime.now(),
            nutrition=nutrition,
            sleep_quality=sleep_quality,
            fitness=fitness,
            stress_level=stress_level,
            ai_recommendation=ai_recommendation
        )

    async def get_user_checkins(
        self,
        user_id,
        skip: int = 0,
        limit: int = 30
    ) -> List[DailyCheckin]:
        """Get all check-ins for specific user."""
        result = await self.db.execute(
            select(DailyCheckin)
            .where(DailyCheckin.user_id == user_id)
            .order_by(DailyCheckin.log_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_latest_checkin(self, user_id: str) -> Optional[DailyCheckin]:
        """Get the most recent check-in for user"""
        result = await self.db.execute(
            select(DailyCheckin)
            .where(DailyCheckin.user_id == user_id)
            .order_by(DailyCheckin.log_date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_checkin_by_date(
            self,
            user_id: str,
            check_date: date
    ) -> Optional[DailyCheckin]:
        """Get check-in for a specific date."""
        # Query for check-ins on the given date
        start_of_day = datetime.combine(check_date, datetime.min.time())
        end_of_day = datetime.combine(check_date, datetime.max.time())

        result = await self.db.execute(
            select(DailyCheckin)
            .where(
                and_(
                    DailyCheckin.user_id == user_id,
                    DailyCheckin.log_date >= start_of_day,
                    DailyCheckin.log_date <= end_of_day
                )
            )
            .order_by(DailyCheckin.log_date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def has_checkin_today(self, user_id: str) -> bool:
        """Check if user has already completed today's check-in."""
        today = date.today()
        checkin = await self.get_checkin_by_date(user_id, today)
        return checkin is not None

    async def get_checkin_streak(self, user_id: str) -> int:
        """Calculate user's consecutive check-in streak"""
        # Get all check=ins ordered by date
        result = await self.db.execute(
            select(DailyCheckin)
            .where(DailyCheckin.user_id == user_id)
            .distinct()
            .order_by(func.date(DailyCheckin.log_date).desc())
        )
        checkin_dates = result.scalars().all()

        if not checkin_dates:
            return 0

        # Calculate streak
        streak = 0
        current_date = date.today()

        for checkin_date in checkin_dates:
            if checkin_date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break

        return streak
