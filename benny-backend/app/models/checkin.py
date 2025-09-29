"""
Database models for daily check-ins.
SQLAlchemy models for PostgreSQL
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


# Enum types for button responses
class NutritionRating(str, enum.Enum):
    """Nutrtion rating options."""
    EXCELLENT = "Excellent"
    GOOD = "Good"
    OKAY = "Okay"
    POOR = "Poor"


class SleepRating(str, enum.Enum):
    """Sleep rating options."""
    VERY_GOOD = "Very good"
    GOOD = "Good"
    OKAY = "Okay"
    POOR = "Poor"


class FitnessCompletion(str, enum.Enum):
    """Fitness activity completion status."""
    COMPLETED = "Yes, completed"
    PARTIALLY = "Partially completed"
    SKIPPED = "No, skipped"


class StressLevel(str, enum.Enum):
    """Stress level rating options."""
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    VERY_HIGH = "Very high"


class DailyCheckin(Base):
    """Daily check-in log entry with button-based responses.
    
    Flow: 
        1. User submits response
        2. Backend saves check-in to DB
        3. Backend calls AI service with check-in data
        4. AI generates personalized recommendation
        5. Backend updates this record with ai_recommendation

    """

    __tablename__ = "daily_checkins"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # User identification
    user_id = Column(String(255), nullable=False, index=True)

    # Timestamp
    log_date = Column(DateTime, nullable=False, default=datetime.now(), index=True)

    # Check-in repsonses
    nutrition = Column(Enum(NutritionRating), nullable=False)
    sleep_quality = Column(Enum(SleepRating), nullable=False)
    fitness = Column(Enum(FitnessCompletion), nullable=False)
    stress_level = Column(Enum(StressLevel), nullable=False)

    # AI recommendation
    ai_recommendation = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return f"<DailyCheckin(id={self.id}, user_id={self.user_id}, date={self.log_date})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "log_date": self.log_date.isoformat(),
            "nutrition": self.nutrition.value,
            "sleep_quality": self.sleep_quality.value,
            "fitness": self.fitness.value,
            "stress_level": self.stress_level.value,
            "ai_recommendation": self.ai_recommendation if self.ai_recommendation else None,
            "created_at": self.created_at.isoformat()
        }