from datetime import date
from typing import Any, Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class AnalyticsRepository:
    """
    Handles analytical queries against analytical database views and materialized views.
    Leverages advanced window functions and CTEs pre-defined in the database.
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_global_kpis(self) -> Optional[Dict[str, Any]]:
        """
        Fetch global summary statistics from the materialized view `mv_global_summary`.
        """
        stmt = text("SELECT * FROM mv_global_summary LIMIT 1")
        result = await self.db.execute(stmt)
        row = result.mappings().first()
        return dict(row) if row else None

    async def get_countries_kpis(
        self,
        continent: Optional[str] = None,
        sort_by: str = "total_cases",
        descending: bool = True,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Fetch country-level snapshots from `mv_country_kpis`.
        """
        order_dir = "DESC" if descending else "ASC"
        # Sanitize sort_by column to avoid SQL injection
        allowed_cols = {
            "total_cases", "total_deaths", "new_cases_7day_avg", "new_deaths_7day_avg",
            "new_cases_per_million", "new_deaths_per_million", "total_cases_per_million",
            "total_deaths_per_million", "reproduction_rate", "stringency_index",
            "case_fatality_rate_pct", "people_fully_vaccinated_per_hundred",
            "positive_rate", "icu_patients_per_million", "hosp_patients_per_million"
        }
        col = sort_by if sort_by in allowed_cols else "total_cases"
        
        query = f"SELECT * FROM mv_country_kpis"
        params: Dict[str, Any] = {"limit": limit, "offset": skip}
        
        if continent:
            query += " WHERE continent = :continent"
            params["continent"] = continent
            
        query += f" ORDER BY {col} {order_dir} NULLS LAST LIMIT :limit OFFSET :offset"
        
        result = await self.db.execute(text(query), params)
        return [dict(row) for row in result.mappings().all()]

    async def get_historical_trends(
        self,
        iso_code: str,
        start_date: date,
        end_date: date,
        metric: str = "new_cases_smoothed"
    ) -> List[Dict[str, Any]]:
        """
        Executes the database-level parameterized function `get_country_trend`
        to fetch daily metric trends with rolling averages and WoW calculations.
        """
        # Sanitization
        allowed_metrics = {
            "new_cases", "new_cases_smoothed", "total_cases", "new_cases_per_million",
            "new_deaths", "new_deaths_smoothed", "total_deaths", "new_deaths_per_million",
            "reproduction_rate", "stringency_index"
        }
        metric_col = metric if metric in allowed_metrics else "new_cases_smoothed"
        
        stmt = text(
            "SELECT * FROM get_country_trend(:iso_code, :start_date, :end_date, :metric)"
        )
        result = await self.db.execute(
            stmt,
            {
                "iso_code": iso_code.upper(),
                "start_date": start_date,
                "end_date": end_date,
                "metric": metric_col
            }
        )
        return [dict(row) for row in result.mappings().all()]

    async def get_continent_kpis(self) -> List[Dict[str, Any]]:
        """
        Fetch continent aggregates from the materialized view `mv_continent_summary`.
        """
        stmt = text("SELECT * FROM mv_continent_summary ORDER BY total_cases DESC")
        result = await self.db.execute(stmt)
        return [dict(row) for row in result.mappings().all()]

    async def get_monthly_trends(
        self,
        iso_code: str,
        start_year_month: Optional[str] = None,
        end_year_month: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve monthly trends per country from `mv_monthly_country_trends`.
        """
        query = "SELECT * FROM mv_monthly_country_trends WHERE iso_code = :iso_code"
        params: Dict[str, Any] = {"iso_code": iso_code.upper()}
        
        if start_year_month:
            query += " AND year_month >= :start_ym"
            params["start_ym"] = start_year_month
        if end_year_month:
            query += " AND year_month <= :end_ym"
            params["end_ym"] = end_year_month
            
        query += " ORDER BY year_month ASC"
        
        result = await self.db.execute(text(query), params)
        return [dict(row) for row in result.mappings().all()]

    async def get_wave_metrics(self, iso_code: str) -> List[Dict[str, Any]]:
        """
        Fetch detected epidemiological wave phases from the view `v_wave_detection`.
        """
        stmt = text(
            "SELECT * FROM v_wave_detection WHERE iso_code = :iso_code ORDER BY date ASC"
        )
        result = await self.db.execute(stmt, {"iso_code": iso_code.upper()})
        return [dict(row) for row in result.mappings().all()]

    async def get_vaccine_equity(self) -> List[Dict[str, Any]]:
        """
        Fetch vaccine equity snapshot by income group from `v_vaccination_equity`.
        """
        stmt = text("SELECT * FROM v_vaccination_equity ORDER BY people_fully_vaccinated_per_hundred DESC")
        result = await self.db.execute(stmt)
        return [dict(row) for row in result.mappings().all()]

    async def get_excess_mortality_burden(self, iso_code: str) -> List[Dict[str, Any]]:
        """
        Fetch mortality excess metrics from `v_excess_burden`.
        """
        stmt = text(
            "SELECT * FROM v_excess_burden WHERE iso_code = :iso_code ORDER BY date ASC"
        )
        result = await self.db.execute(stmt, {"iso_code": iso_code.upper()})
        return [dict(row) for row in result.mappings().all()]

    async def get_policy_stringency_correlation(self) -> List[Dict[str, Any]]:
        """
        Fetch policy stringency correlation dataset from `v_stringency_vs_cases`.
        """
        stmt = text("SELECT * FROM v_stringency_vs_cases ORDER BY year_month ASC")
        result = await self.db.execute(stmt)
        return [dict(row) for row in result.mappings().all()]
