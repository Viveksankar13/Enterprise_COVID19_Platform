from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.vaccination_repository import VaccinationRepository
from app.repositories.analytics_repository import AnalyticsRepository
from app.api.v1.dependencies.auth import get_current_user
from app.core.cache import cache_response

router = APIRouter()


@router.get("/equity", summary="Get vaccine equity aggregates by income group")
@cache_response(expire_seconds=600)
async def get_vaccine_equity(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """
    Returns global vaccination coverage comparison across economic income groups.
    """
    repo = AnalyticsRepository(db)
    return await repo.get_vaccine_equity()


@router.get("/history", summary="Get country vaccination timeline history")
@cache_response(expire_seconds=300)
async def get_vaccination_history(
    request: Request,
    iso_code: str = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """
    Retrieves full chronological daily vaccination timeline for a country.
    """
    repo = VaccinationRepository(db)
    history = await repo.get_country_history(iso_code=iso_code, start_date=start_date, end_date=end_date)
    return history
