"""
Pydantic schemas for check-in requestions and responses.
Validates API input/output
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


# Request schemas
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


class StressLevel(str, Enum):
    """Stress level rating options."""
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    VERY_HIGH = "Very high"


class CheckinResponse(BaseModel):
    """Individual question response from frontend."""
    category: str
    response: str

    @validator
    def validate_response(cls, v, values):
        """Ensure response matches valid button options."""
        category = values.get('category')
        valid_responses = {
            'nutrition': [e.value for e in NutritionRating],
            'sleep': [e.value for e in SleepRating],
            'fitness': [e.value for e in FitnessCompletion],
            'stress': [e.value for e in StressLevel]
        }

        if category in valid_responses and v not in valid_responses[category]:
            raise ValueError(f'Invalid response for {category}: {v}')

        return v


class CheckInSubmission(BaseModel):
    """Complete check-in submission from frontend."""
    responses: List[CheckinResponse] = Field(..., min_items=4, max_items=4)

    @validator
    def validate_all_categories(cls, v):
        """Ensure all required categories are present."""
        categories = {r.category for r in v}
        required = {'nutrition', 'sleep', 'fitness', 'stress'}

        if categories != required:
            missing = required - categories
            extra = categories - required
            errors = []
            if missing:
                errors.append(f"Missing categories: {missing}")
            if extra:
                errors.append(f"Extra categories: {extra}")
            raise ValueError('; '.join(errors))

        return v


class CheckInResult(BaseModel):
    """Response after successful check-in."""
    success: bool
    message: str
    checkin_id: int
    ai_recommendation: Optional[str] = None

    class Config:
        from_attributes = True


class CheckInHistory(BaseModel):
    """Check-in history item for display."""
    id: int
    log_date: datetime
    nutrition: str
    sleep_quality: str
    fitness: str
    stress_level: str
    ai_recommendation: Optional[str] = None

    class Config:
        from_attributes = True

