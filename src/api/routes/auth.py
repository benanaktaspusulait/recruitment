from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from src.database import get_db
from src.services.auth_service import AuthService
from src.models import schemas
from src.core.config import get_settings
from src.models import entities

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/token",
    response_model=schemas.Token,
    summary="Create access token",
    description="Create access token for user authentication",
    responses={
        200: {
            "description": "Successful authentication",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect username or password"}
                }
            }
        }
    }
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Create access token for user authentication.
    
    - **username**: Email address
    - **password**: User password
    """
    user = await AuthService.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = AuthService.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get(
    "/me",
    response_model=schemas.User,
    summary="Get current user",
    description="Get details of currently authenticated user",
    responses={
        200: {
            "description": "Current user details",
            "content": {
                "application/json": {
                    "example": {
                        "email": "user@example.com",
                        "role": "ADMIN",
                        "is_active": True,
                        "id": 1,
                        "created_at": "2024-03-14T12:00:00Z"
                    }
                }
            }
        },
        401: {"description": "Not authenticated"},
        400: {"description": "Inactive user"}
    }
)
async def read_users_me(
    current_user: schemas.User = Depends(AuthService.get_current_active_user)
):
    """
    Get details of currently authenticated user.
    
    Requires valid JWT token in Authorization header.
    """
    return current_user 

@router.get("/debug/users", tags=["Debug"])
async def list_users(db: Session = Depends(get_db)):
    """Debug endpoint to list all users - remove in production"""
    users = db.query(entities.User).all()
    return [{
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active
    } for user in users] 