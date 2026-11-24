from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.v1.dependencies.auth import get_current_user
from app.core.cache import cache_response

router = APIRouter()


@router.get("/summary", summary="Get high level system metrics summary")
@cache_response(expire_seconds=300)
async def get_kpi_summary(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """
    Returns platform-wide summary counts of records and ingest logs.
    """
    # Run dynamic counts of the database load
    result = await db.execute(text("SELECT count(*) FROM countries"))
    countries_count = result.scalar()
    
    result = await db.execute(text("SELECT count(*) FROM daily_metrics"))
    metrics_count = result.scalar()
    
    result = await db.execute(text("SELECT count(*) FROM etl_logs"))
    etl_count = result.scalar()
    
    result = await db.execute(text("SELECT count(*) FROM users"))
    users_count = result.scalar()

    return {
        "countries_registered": countries_count,
        "epidemiological_records": metrics_count,
        "ingestion_runs": etl_count,
        "platform_users": users_count
    }
