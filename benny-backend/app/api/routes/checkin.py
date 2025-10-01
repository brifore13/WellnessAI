"""
Check-in API endpoints.
Handles daily wellness check-in submissions and history.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.checkin import (
    CheckInSubmission,
    CheckInResult,
    CheckInHistoryResponse,
    CheckInHistoryItem,
    UserStreakResponse
)
from app.services.checkin import CheckinService, DuplicateCheckinError
from app.services.dependencies import get_checkin_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/checkin", tags=["checkin"])


@router.post("/submit", response_model=CheckInResult, status_code=status.HTTP_201_CREATED)
async def submit_checkin(
    submission: CheckInSubmission,
    service: CheckinService = Depends(get_checkin_service)
    # TODO: Add authentication: current_user: dict = Depends(get_current_user)
):
    """
    Submit daily check-in responses.

    This is the main check-in endpoint that:
    1. Validates responses (automatic via Pydantic)
    2. Saves check-in to database
    3. Gets AI recommendation
    4. Returns result

    """
    # TODO: Get user_id from authentication
    # For now, use a placeholder
    user_id = "demo_user"  # Replace with: current_user['user']['sub']

    try:
        # Convert frontend format to service format
        checkin_data = {r.category: r.response for r in submission.responses}

        # Submit to service
        checkin = await service.submit_checkin(
            user_id=user_id,
            nutrition=checkin_data.get("nutrition"),
            sleep_quality=checkin_data.get("sleep"),
            fitness=checkin_data.get("fitness"),
            stress_level=checkin_data.get("stress")
        )

        logger.info(f"Check-in {checkin.id} created successfully")

        return CheckInResult(
            success=True,
            message="Check-in saved successfully!",
            checkin_id=checkin.id,
            recommendation=checkin.ai_recommendation
        )

    except DuplicateCheckinError as e:
        logger.warning(f"Duplicate check-in attempt by user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    except ValueError as e:
        logger.error(f"Invalid check-in data: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

    except Exception as e:
        logger.error(f"Unexpected error in check-in submission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process check-in"
        )


@router.get("/history", response_model=CheckInHistoryResponse)
async def get_checkin_history(
    limit: int = 30,
    service: CheckinService = Depends(get_checkin_service)
    # TODO: Add authentication: current_user: dict = Depends(get_current_user)
):
    """
    Get user's check-in history.

    Returns up to 'limit' most recent check-ins for the user.
    """
    # TODO: Get user_id from authentication
    user_id = "demo_user"

    try:
        checkins = await service.get_user_history(user_id, limit=limit)

        # Convert to response format
        history_items = [
            CheckInHistoryItem(
                id=c.id,
                log_date=c.log_date,
                nutrition=c.nutrition.value,
                sleep_quality=c.sleep_quality.value,
                fitness=c.fitness.value,
                stress_level=c.stress_level.value,
                ai_recommendation=c.ai_recommendation
            )
            for c in checkins
        ]

        return CheckInHistoryResponse(
            success=True,
            checkins=history_items,
            count=len(history_items)
        )

    except Exception as e:
        logger.error(f"Error fetching check-in history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch check-in history"
        )


@router.get("/streak", response_model=UserStreakResponse)
async def get_user_streak(
    service: CheckinService = Depends(get_checkin_service)
    # TODO: Add authentication: current_user: dict = Depends(get_current_user)
):
    """
    Get user's current check-in streak.

    Returns the number of consecutive days the user has completed check-ins.
    """
    # TODO: Get user_id from authentication
    user_id = "demo_user"

    try:
        streak = await service.get_user_streak(user_id)

        if streak == 0:
            message = "Start your streak today!"
        elif streak == 1:
            message = "Great start! Keep it going!"
        else:
            message = f"Amazing! {streak} days strong! 🔥"

        return UserStreakResponse(
            success=True,
            streak=streak,
            message=message
        )

    except Exception as e:
        logger.error(f"Error fetching streak: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch streak"
        )
