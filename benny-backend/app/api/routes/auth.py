"""
Authentication API endpoints.
Handles user registration, login, and demo access.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.services.auth import AuthService, AuthenticationError
from app.services.dependencies import get_auth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


# Schemas
class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User information response."""
    id: int
    email: str
    username: str
    is_demo: bool
    is_active: bool
    created_at: str


class AuthResponse(BaseModel):
    """Authentication response with token."""
    success: bool
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
    is_demo: bool = False


# Endpoints
@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user account.
    
    Creates a new user with email, username, and password.
    Returns access token for immediate login.
    """
    try:
        result = await auth_service.register_user(
            email=request.email,
            username=request.username,
            password=request.password
        )
        
        return AuthResponse(
            success=True,
            user=UserResponse(**result["user"]),
            access_token=result["access_token"],
            token_type=result["token_type"]
        )
        
    except AuthenticationError as e:
        logger.warning(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login with email and password.
    
    Returns access token on successful authentication.
    """
    try:
        result = await auth_service.login(
            email=request.email,
            password=request.password
        )
        
        return AuthResponse(
            success=True,
            user=UserResponse(**result["user"]),
            access_token=result["access_token"],
            token_type=result["token_type"]
        )
        
    except AuthenticationError as e:
        logger.warning(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login"
        )


@router.post("/demo", response_model=AuthResponse)
async def demo_login(
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login as demo user - no credentials required.
    
    Perfect for employers and testers to try the app instantly.
    Demo user shares data across all demo sessions.
    """
    try:
        result = await auth_service.demo_login()
        
        logger.info("Demo session created")
        
        return AuthResponse(
            success=True,
            user=UserResponse(**result["user"]),
            access_token=result["access_token"],
            token_type=result["token_type"],
            is_demo=True
        )
        
    except Exception as e:
        logger.error(f"Demo login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create demo session"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Requires valid access token in Authorization header.
    """
    return UserResponse(**user.to_dict())