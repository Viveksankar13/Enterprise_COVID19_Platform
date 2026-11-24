from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from app.database.session import get_db
from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.authentication.jwt import (
    verify_password,
    create_jwt_token,
    decode_jwt_token,
)
from app.schemas.auth import UserLogin, TokenResponse, UserOut
from app.api.v1.dependencies.auth import get_current_user
from app.models.user import User
from jose import JWTError

router = APIRouter()


@router.post("/login", response_model=TokenResponse, summary="Sign in to platform")
async def login(
    login_data: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticates username and password. Returns access token, refresh token, and user info.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(login_data.username)
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    # Increment login metrics
    await user_repo.increment_login_stats(user, datetime.now(timezone.utc))
    
    # Sign tokens
    access_token = create_jwt_token(data={"sub": user.username}, token_type="access")
    refresh_token = create_jwt_token(data={"sub": user.username}, token_type="refresh")
    
    # Store refresh token in HTTP-only cookie for secure rotation
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.APP_ENV == "production",  # Set True in production (requires HTTPS)
        samesite="lax",
        max_age=7 * 24 * 3600  # 7 days
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/refresh", summary="Renew expired access token")
async def refresh(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Extracts refresh token from cookies and issues a new access token.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing"
        )
        
    try:
        payload = decode_jwt_token(refresh_token)
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token type"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token credentials"
        )
        
    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(username)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token is invalid or deactivated"
        )
        
    new_access_token = create_jwt_token(data={"sub": user.username}, token_type="access")
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut, summary="Get current logged in user details")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns user details profile for the authenticated session.
    """
    return current_user
