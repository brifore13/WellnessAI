"""
Benny AI Service API
Microservice for AI-powered wellness recommendations and chat.
"""
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from src.core.benny import BennyWellnessAI
from src.core.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global Benny instance
benny: Optional[BennyWellnessAI] = None


# Pydantic Schemas
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)


class DailyCheckInData(BaseModel):
    nutrition: str
    sleep: str
    fitness: str
    stress : str


class ChatResponse(BaseModel):
    success: bool
    response: str
    tokens_used: int = 0
    error: Optional[str] = None


class RecommendationRequest(BaseModel):
    daily_checkin: DailyCheckInData


# Application Lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize Benny when API starts"""
    global benny
    try:
        logger.info("Initializing Benny AI...")
        benny = BennyWellnessAI()
        logger.info("Benny AI ready!")
    except Exception as e:
        logger.error(f"Failed to initialize Benny: {e}")
        raise

    yield

    logger.info("Shutting down Benny AI service")

# FastAPI Application
app = FastAPI(
    title="Benny Wellness AI",
    version="1.2.0",
    description="AI microservice for wellness coaching",
    lifespan=lifespan
)


# CORS Configuration
@property
def allowed_origins():
    """Get allowed CORS origins."""
    return [
        settings.frontend_url,
        settings.backend_url,
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000"
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        settings.backend_url,
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)


# API ENDPOINTS
@app.get("/")
async def root():
    """Service information endpoint"""
    return {
        "service": "Benny Wellness AI",
        "version": "1.2.0",
        "endpoints": {
            "chat": "/chat",
            "recommend": "/recommend",
            "health": "/heath",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Benny health check"""
    return {"status": "healthy", "benny_ready": benny is not None}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with Benny AI
    """
    # Benny not responding
    if not benny:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not initialized"
        )

    try:
        result = await benny.chat(request.message)

        return ChatResponse(
            success=result["success"],
            response=result.get("response", ""),
            tokens_used=result.get("tokens_used", 0),
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat request"
        )


@app.post("/recommend", response_model=ChatResponse)
async def recommend(request: RecommendationRequest):
    """
    Get wellness recommendation based on daily check-in.
    Analyzes check-in data and provides targeted wellness advide
    """
    if not benny:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not initialized"
        )
    try:
        result = await benny.recommend(
            request.daily_checkin.model_dump()
        )
        
        return ChatResponse(
            success=result["success"],
            response=result.get("response", ""),
            tokens_used=result.get("tokens_used", 0),
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process recommendation request"
        )


if __name__ == "__main__":
    logger.info(f"Starting Benny AI Service on {settings.host}:{settings.port}")
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )