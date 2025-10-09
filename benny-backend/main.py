"""
Benny Wellness AI Backend - Main Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.database import startup_database, shutdown_database
from app.core.logging import setup_logging

# Import routers
from app.api.routes import health, checkin, auth, chat
from routers import auth, users

# Setup logging
setup_logging(debug=settings.debug)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    logger.info("Starting Benny Wellness AI Backend...")
    await startup_database()
    logger.info("Application started successfully")
    
    yield
    
    logger.info("Shutting down application...")
    await shutdown_database()
    logger.info("Application shut down complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# Session middleware
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Include routers
app.include_router(health.router)
app.include_router(checkin.router)
app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(users.router)


if __name__ == "__main__":
    logger.info(f"Starting {settings.app_name}...")
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )