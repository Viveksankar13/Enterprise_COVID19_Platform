from typing import List, Optional
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.country import Country
from app.repositories.base import BaseRepository


class CountryRepository(BaseRepository[Country]):
    """
    Repository for managing Country records, supporting advanced filtering, searches, and continent aggregates.
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(Country, db_session)

    async def list_active(
        self,
        continent: Optional[str] = None,
        include_aggregates: bool = False,
        search_query: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Country]:
        """
        List active countries with optional continent filtering and search matching.
        """
        stmt = select(Country).where(Country.is_active == True)
        
        if not include_aggregates:
            stmt = stmt.where(Country.is_aggregate == False)
            
        if continent:
            stmt = stmt.where(Country.continent == continent)
            
        if search_query:
            # Use ILIKE comparison on location/iso_code
            stmt = stmt.where(
                or_(
                    Country.location.ilike(f"%{search_query}%"),
                    Country.iso_code.ilike(f"%{search_query}%")
                )
            )
            
        stmt = stmt.order_by(Country.location).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_iso(self, iso_code: str) -> Optional[Country]:
        """
        Retrieves a country by its unique uppercase ISO code.
        """
        return await self.get(iso_code.upper())

    async def get_continents(self) -> List[str]:
        """
        Lists distinct continents present in the countries database.
        """
        stmt = select(Country.continent).where(
            Country.continent.isnot(None)
        ).distinct().order_by(Country.continent)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
