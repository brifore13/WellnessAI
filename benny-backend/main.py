# Imports & Dependencies
# Standard library imports
import datetime
import logging
import contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional

# Third-party imports
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Local imports
from app.core.config import settings
from app.core.database import startup_database, shutdown_database
from app.core.logging import setup_logging
from routers import auth, users

# Setup logging
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown."""
    logger.info("Starting application...")
    await startup_database()
    yield
    logger.info("Shutting down...")
    await shutdown_database()


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {"service": settings.app_name, "status": "running"}

@app.get("/health")
async def health_check():
    return { "status": "healthy" }


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)