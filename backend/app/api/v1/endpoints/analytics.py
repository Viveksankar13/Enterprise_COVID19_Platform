from datetime import date, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.analytics_repository import AnalyticsRepository
from app.api.v1.dependencies.auth import get_current_user
from app.core.cache import cache_response

router = APIRouter()


@router.get("/global", summary="Get global summary KPIs")
@cache_response(expire_seconds=600)  # Cache for 10 minutes
async def get_global_kpi(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """
    Retrieves global cumulative aggregates from materialized view.
    """
    repo = AnalyticsRepository(db)
    data = await repo.get_global_kpis()
    if not data:
        raise HTTPException(status_code=404, detail="Global KPIs summary not found")
    return data


@router.get("/countries", summary="List country-level KPI snapshots")
@cache_response(expire_seconds=300)  # Cache for 5 minutes
async def get_countries_kpis(
    request: Request,
    continent: Optional[str] = Query(None),
    sort_by: str = Query("total_cases"),
    descending: bool = Query(True),
    limit: int = Query(50, ge=1, le=250),
    skip: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """
    Returns high-level snapshot data for all active countries.
    """
    repo = AnalyticsRepository(db)
    return await repo.get_countries_kpis(
        continent=continent,
        sort_by=sort_by,
        descending=descending,
        limit=limit,
        skip=skip
    )


@router.get("/continents", summary="Get continent-level aggregates")
@cache_response(expire_seconds=600)
async def get_continents_kpis(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """
    Returns cumulative summaries grouped by continent.
    """
    repo = AnalyticsRepository(db)
    return await repo.get_continent_kpis()


@router.get("/trends/historical", summary="Get daily metric historical trends")
@cache_response(expire_seconds=300)
async def get_historical_trends(
    request: Request,
    iso_code: str = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    metric: str = Query("new_cases_smoothed"),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """
    Invokes specialized get_country_trend database-level function.
    """
    repo = AnalyticsRepository(db)
    # Default start date is 2020-01-01, end date is today
    s_date = start_date or date(2020, 1, 1)
    e_date = end_date or date.today()
    return await repo.get_historical_trends(
        iso_code=iso_code,
        start_date=s_date,
        end_date=e_date,
        metric=metric
    )


@router.get("/trends/monthly", summary="Get monthly aggregates per country")
@cache_response(expire_seconds=600)
async def get_monthly_trends(
    request: Request,
    iso_code: str = Query(...),
    start_ym: Optional[str] = Query(None, description="Format YYYY-MM"),
    end_ym: Optional[str] = Query(None, description="Format YYYY-MM"),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """
    Returns monthly case/death totals and vaccination rollouts.
    """
    repo = AnalyticsRepository(db)
    return await repo.get_monthly_trends(
        iso_code=iso_code,
        start_year_month=start_ym,
        end_year_month=end_ym
    )


@router.get("/epidemic/waves", summary="Detect wave phases")
@cache_response(expire_seconds=600)
async def get_epidemic_waves(
    request: Request,
    iso_code: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """
    Returns starting dates, peaks, and sizes of wave cycles.
    """
    repo = AnalyticsRepository(db)
    return await repo.get_wave_metrics(iso_code=iso_code)


@router.get("/mortality/excess", summary="Get CFR & excess mortality details")
@cache_response(expire_seconds=600)
async def get_excess_mortality(
    request: Request,
    iso_code: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """
    Returns Case Fatality Rate (CFR) and severity metrics.
    """
    repo = AnalyticsRepository(db)
    return await repo.get_excess_mortality_burden(iso_code=iso_code)


@router.get("/correlations/stringency", summary="Policy stringency vs case rates correlation")
@cache_response(expire_seconds=600)
async def get_stringency_correlation(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """
    Returns correlation series between containment policies and case rates.
    """
    repo = AnalyticsRepository(db)
    return await repo.get_policy_stringency_correlation()
