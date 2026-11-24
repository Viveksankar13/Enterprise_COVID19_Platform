from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.hospitalization import Hospitalization
from app.api.v1.dependencies.auth import get_current_user
from app.core.cache import cache_response

router = APIRouter()


@router.get("", summary="Get country hospitalization timeline history")
@cache_response(expire_seconds=300)
async def get_hospitalization_history(
    request: Request,
    iso_code: str = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """
    Retrieves the ICU and hospitalization occupancy rates timeline for a country.
    """
    stmt = select(Hospitalization).where(Hospitalization.iso_code == iso_code.upper())
    if start_date:
        stmt = stmt.where(Hospitalization.date >= start_date)
    if end_date:
        stmt = stmt.where(Hospitalization.date <= end_date)
        
    stmt = stmt.order_by(Hospitalization.date.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())
