from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings
import redis

# Hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Optional Redis connection for token blacklisting (e.g., logout tracking)
try:
    redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception:
    redis_client = None


def hash_password(password: str) -> str:
    """
    Hashes a cleartext password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a cleartext password against a hashed value.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None, token_type: str = "access") -> str:
    """
    Signs and packages a JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        if token_type == "access":
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        else:
            expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": token_type})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT token.
    Raises JWTError if invalid or expired.
    """
    # Check if blacklisted in Redis
    if redis_client:
        try:
            if redis_client.get(f"blacklist:{token}"):
                raise JWTError("Token is blacklisted")
        except Exception:
            pass  # Fallback gracefully if Redis is down

    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return payload


def blacklist_jwt_token(token: str, expires_in_seconds: int) -> None:
    """
    Adds a JWT token to the Redis blacklist to revoke it immediately.
    """
    if redis_client:
        try:
            redis_client.setex(f"blacklist:{token}", expires_in_seconds, "true")
        except Exception:
            pass
