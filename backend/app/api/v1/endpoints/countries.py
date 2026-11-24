from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.country_repository import CountryRepository
from app.schemas.country import CountryOut
from app.api.v1.dependencies.auth import get_current_user

router = APIRouter()


@router.get("", response_model=List[CountryOut], summary="List all active countries")
async def list_countries(
    continent: Optional[str] = Query(None, description="Filter by continent"),
    search: Optional[str] = Query(None, description="Search by location name or ISO code"),
    include_aggregates: bool = Query(False, description="Whether to include regional aggregates"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=250),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """
    Returns a list of active countries from dimensions, filtered by continent or search query.
    """
    repo = CountryRepository(db)
    return await repo.list_active(
        continent=continent,
        include_aggregates=include_aggregates,
        search_query=search,
        skip=skip,
        limit=limit
    )


@router.get("/continents", response_model=List[str], summary="Get distinct continents list")
async def get_continents(
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """
    Returns list of distinct continents in database.
    """
    repo = CountryRepository(db)
    return await repo.get_continents()


@router.get("/{iso_code}", response_model=CountryOut, summary="Get country by ISO code")
async def get_country(
    iso_code: str,
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """
    Retrieves country metadata by its ISO-3166 alphabetic code.
    """
    repo = CountryRepository(db)
    country = await repo.get_by_iso(iso_code)
    if not country:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Country not found")
    return country
