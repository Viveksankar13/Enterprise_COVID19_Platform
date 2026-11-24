from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.user_repository import UserRepository
from app.authentication.jwt import decode_jwt_token
from app.models.user import User

# OAuth2 scheme config
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"/api/v1/auth/login",
    auto_error=False  # Allow fallback or custom cookie checks if needed
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Extracts the authentication token, decodes it, and returns the current user profile.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception

    try:
        payload = decode_jwt_token(token)
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(username)
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="User account is deactivated"
        )
        
    return user


class PermissionChecker:
    """
    FastAPI dependency that enforces Role-Based Access Control (RBAC).
    Verifies if the current user possesses permission for a given resource and action.
    """

    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # Admin bypasses all checks
        if current_user.role.name == "admin":
            return current_user

        user_repo = UserRepository(db)
        permissions = await user_repo.get_permissions_for_role(current_user.role_id)
        
        # Check permission matrix matching resource and action
        for perm in permissions:
            if perm.resource == self.resource and perm.action == self.action:
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access Denied: Required privilege ({self.resource}:{self.action}) missing."
        )
