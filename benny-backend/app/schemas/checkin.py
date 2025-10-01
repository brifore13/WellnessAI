"""
Pydantic schemas for check-in API endpoints.
These define the API contract - what goes in and out.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


# Enums matching frontend button options
class NutritionRating(str, Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    OKAY = "Okay"
    POOR = "Poor"


class SleepRating(str, Enum):
    VERY_GOOD = "Very good"
    GOOD = "Good"
    OKAY = "Okay"
    POOR = "Poor"


class FitnessCompletion(str, Enum):
    COMPLETED = "Yes, completed"
    PARTIALLY = "Partially completed"
    SKIPPED = "No, skipped"


class StressLevel(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    VERY_HIGH = "Very high"


# Request/Response Schemas
class CheckInResponse(BaseModel):
    """Individual question response from frontend."""
    category: str
    response: str


class CheckInSubmission(BaseModel):
    """Complete check-in submission from frontend."""
    responses: List[CheckInResponse] = Field(..., min_length=4, max_length=4)
    
    @validator('responses')
    def validate_categories(cls, v):
        """Ensure all required categories present and no duplicates."""
        categories = [r.category for r in v]
        required = {'nutrition', 'sleep', 'fitness', 'stress'}
        
        # Check for duplicates
        if len(categories) != len(set(categories)):
            raise ValueError('Duplicate categories not allowed')
        
        # Check all required present
        provided = set(categories)
        if provided != required:
            missing = required - provided
            extra = provided - required
            errors = []
            if missing:
                errors.append(f"Missing: {', '.join(missing)}")
            if extra:
                errors.append(f"Invalid: {', '.join(extra)}")
            raise ValueError('; '.join(errors))
        
        return v


class CheckInResult(BaseModel):
    """Response after successful check-in submission."""
    success: bool
    message: str
    checkin_id: int
    recommendation: Optional[str] = None
    
    class Config:
        from_attributes = True  # Allows converting from SQLAlchemy models


class CheckInHistoryItem(BaseModel):
    """Single check-in in history list."""
    id: int
    log_date: datetime
    nutrition: str
    sleep_quality: str
    fitness: str
    stress_level: str
    ai_recommendation: Optional[str] = None
    
    class Config:
        from_attributes = True


class CheckInHistoryResponse(BaseModel):
    """Response containing user's check-in history."""
    success: bool
    checkins: List[CheckInHistoryItem]
    count: int


class UserStreakResponse(BaseModel):
    """Response with user's check-in streak."""
    success: bool
    streak: int
    message: str