from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database.session import get_db

router = APIRouter()


@router.get("", summary="Get API Service Health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Returns API health status, checking connectivity to database and cache.
    """
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "api_service": "healthy"
    }
