"""
Demographic ORM model — maps to the `demographics` table.
One row per country. Contains population, socioeconomic, and health indicators.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.country import Country


class Demographic(Base):
    """Population and socioeconomic indicators. One-to-one with Country."""

    __tablename__ = "demographics"

    iso_code: Mapped[str] = mapped_column(
        String(8),
        ForeignKey("countries.iso_code", ondelete="CASCADE"),
        primary_key=True,
    )

    population: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    population_density: Mapped[Optional[float]] = mapped_column(Numeric(10, 3), nullable=True)
    median_age: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    aged_65_older: Mapped[Optional[float]] = mapped_column(Numeric(6, 3), nullable=True)
    aged_70_older: Mapped[Optional[float]] = mapped_column(Numeric(6, 3), nullable=True)
    gdp_per_capita: Mapped[Optional[float]] = mapped_column(Numeric(12, 3), nullable=True)
    extreme_poverty: Mapped[Optional[float]] = mapped_column(Numeric(6, 3), nullable=True)
    cardiovasc_death_rate: Mapped[Optional[float]] = mapped_column(Numeric(8, 3), nullable=True)
    diabetes_prevalence: Mapped[Optional[float]] = mapped_column(Numeric(6, 3), nullable=True)
    female_smokers: Mapped[Optional[float]] = mapped_column(Numeric(6, 3), nullable=True)
    male_smokers: Mapped[Optional[float]] = mapped_column(Numeric(6, 3), nullable=True)
    handwashing_facilities: Mapped[Optional[float]] = mapped_column(Numeric(6, 3), nullable=True)
    hospital_beds_per_thousand: Mapped[Optional[float]] = mapped_column(Numeric(6, 3), nullable=True)
    life_expectancy: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    human_development_index: Mapped[Optional[float]] = mapped_column(Numeric(5, 4), nullable=True)
    data_year: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    country: Mapped["Country"] = relationship("Country", back_populates="demographic")

    def __repr__(self) -> str:
        return f"<Demographic iso={self.iso_code!r} pop={self.population} hdi={self.human_development_index}>"
