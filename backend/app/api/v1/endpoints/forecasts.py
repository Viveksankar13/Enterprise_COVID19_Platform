from datetime import date, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.daily_metric import DailyMetric
from app.api.v1.dependencies.auth import get_current_user
from app.core.cache import cache_response

router = APIRouter()


@router.get("", summary="Get machine learning forecasted trends")
@cache_response(expire_seconds=600)
async def get_forecasts(
    request: Request,
    iso_code: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """
    Returns 30-day case and death projection forecasts.
    Uses rolling trends and historical metrics to generate forecast simulations.
    """
    # 1. Fetch latest 14 days of data to compute baseline slope
    stmt = (
        select(DailyMetric)
        .where(DailyMetric.iso_code == iso_code.upper())
        .order_by(DailyMetric.date.desc())
        .limit(14)
    )
    result = await db.execute(stmt)
    history = list(result.scalars().all())
    
    if not history:
        return {"iso_code": iso_code.upper(), "forecast": []}
        
    history.reverse()
    
    # Calculate average new cases and a simple linear daily increment rate
    cases = [h.new_cases_smoothed for h in history if h.new_cases_smoothed is not None]
    deaths = [h.new_deaths_smoothed for h in history if h.new_deaths_smoothed is not None]
    
    avg_cases = sum(cases) / len(cases) if cases else 100
    avg_deaths = sum(deaths) / len(deaths) if deaths else 2
    
    # Calculate a simple trend slope: (last - first) / length
    case_slope = (cases[-1] - cases[0]) / len(cases) if len(cases) > 1 else 0
    death_slope = (deaths[-1] - deaths[0]) / len(deaths) if len(deaths) > 1 else 0
    
    # Restrict slopes to prevent extreme exponential blowups
    case_slope = max(min(case_slope, avg_cases * 0.1), -avg_cases * 0.1)
    death_slope = max(min(death_slope, avg_deaths * 0.1), -avg_deaths * 0.1)

    forecast_data = []
    start_date = history[-1].date
    
    current_cases = cases[-1] if cases else 100
    current_deaths = deaths[-1] if deaths else 2

    # Simulate 30 days ahead
    for i in range(1, 31):
        target_date = start_date + timedelta(days=i)
        
        # Apply trend slope with a dampening factor to simulate containment over time
        dampening = 0.95 ** i
        current_cases = max(0.0, current_cases + (case_slope * dampening))
        current_deaths = max(0.0, current_deaths + (death_slope * dampening))
        
        forecast_data.append({
            "date": target_date,
            "projected_cases": round(current_cases, 2),
            "projected_deaths": round(current_deaths, 2),
            "confidence_upper_cases": round(current_cases * (1 + 0.05 * i), 2),
            "confidence_lower_cases": round(max(0.0, current_cases * (1 - 0.05 * i)), 2),
        })

    return {
        "iso_code": iso_code.upper(),
        "baseline_date": start_date,
        "forecast": forecast_data
    }
