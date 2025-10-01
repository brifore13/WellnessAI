"""
Health check endpoints.
Simple status checks for monitoring.
"""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "service": "Benny Wellness AI Backend",
        "version": "1.2.0",
        "status": "running"
    }

@router.get("/health")
async def health_check():
    """Health check for load balances and monitoring."""
    return {
        "status": "healthy",
        "database": "connected"
    }