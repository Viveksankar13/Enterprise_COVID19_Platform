"""
Vaccination ORM model — maps to the `vaccinations` table.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.country import Country


class Vaccination(Base):
    """Vaccination program data. Composite PK: (iso_code, date)."""

    __tablename__ = "vaccinations"

    iso_code: Mapped[str] = mapped_column(
        String(8), ForeignKey("countries.iso_code"), primary_key=True
    )
    date: Mapped[date] = mapped_column(
        Date, ForeignKey("calendar.date_value"), primary_key=True, index=True
    )

    # ── Raw Counts ────────────────────────────────────────────────────────────
    total_vaccinations: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    people_vaccinated: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    people_fully_vaccinated: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    total_boosters: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    new_vaccinations: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    new_vaccinations_smoothed: Mapped[Optional[float]] = mapped_column(Numeric(14, 3), nullable=True)

    # ── Per-100 Rates ─────────────────────────────────────────────────────────
    total_vaccinations_per_hundred: Mapped[Optional[float]] = mapped_column(Numeric(8, 3), nullable=True)
    people_vaccinated_per_hundred: Mapped[Optional[float]] = mapped_column(Numeric(8, 3), nullable=True)
    people_fully_vaccinated_per_hundred: Mapped[Optional[float]] = mapped_column(Numeric(8, 3), nullable=True)
    total_boosters_per_hundred: Mapped[Optional[float]] = mapped_column(Numeric(8, 3), nullable=True)
    new_vaccinations_smoothed_per_million: Mapped[Optional[float]] = mapped_column(Numeric(12, 3), nullable=True)

    # ── Audit ─────────────────────────────────────────────────────────────────
    etl_run_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    loaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    country: Mapped["Country"] = relationship("Country", back_populates="vaccinations")

    def __repr__(self) -> str:
        return (
            f"<Vaccination iso={self.iso_code!r} date={self.date} "
            f"fully_vacc_pct={self.people_fully_vaccinated_per_hundred}>"
        )
