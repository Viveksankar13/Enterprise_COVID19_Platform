from datetime import date
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.vaccination import Vaccination
from app.repositories.base import BaseRepository


class VaccinationRepository(BaseRepository[Vaccination]):
    """
    Repository for managing Vaccination fact data.
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(Vaccination, db_session)

    async def get_by_country_and_date(
        self, iso_code: str, target_date: date
    ) -> Optional[Vaccination]:
        """
        Retrieves vaccination data for a specific country and date.
        """
        stmt = select(Vaccination).where(
            Vaccination.iso_code == iso_code.upper(),
            Vaccination.date == target_date
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_country_history(
        self, iso_code: str, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[Vaccination]:
        """
        Retrieves the timeline of vaccination metrics for a given country.
        """
        stmt = select(Vaccination).where(Vaccination.iso_code == iso_code.upper())
        if start_date:
            stmt = stmt.where(Vaccination.date >= start_date)
        if end_date:
            stmt = stmt.where(Vaccination.date <= end_date)
            
        stmt = stmt.order_by(Vaccination.date.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
