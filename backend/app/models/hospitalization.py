"""
Hospitalization ORM model — maps to the `hospitalizations` table.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import (
    CheckConstraint, Date, DateTime, ForeignKey,
    Integer, Numeric, String, func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.country import Country


class Hospitalization(Base):
    """Hospital and ICU capacity metrics. Composite PK: (iso_code, date)."""

    __tablename__ = "hospitalizations"
    __table_args__ = (
        CheckConstraint("icu_patients IS NULL OR icu_patients >= 0",  name="icu_nonneg"),
        CheckConstraint("hosp_patients IS NULL OR hosp_patients >= 0", name="hosp_nonneg"),
    )

    iso_code: Mapped[str] = mapped_column(
        String(8), ForeignKey("countries.iso_code"), primary_key=True
    )
    date: Mapped[date] = mapped_column(
        Date, ForeignKey("calendar.date_value"), primary_key=True, index=True
    )

    icu_patients: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    icu_patients_per_million: Mapped[Optional[float]] = mapped_column(Numeric(10, 3), nullable=True)
    hosp_patients: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    hosp_patients_per_million: Mapped[Optional[float]] = mapped_column(Numeric(10, 3), nullable=True)
    weekly_icu_admissions: Mapped[Optional[float]] = mapped_column(Numeric(12, 3), nullable=True)
    weekly_icu_admissions_per_million: Mapped[Optional[float]] = mapped_column(Numeric(10, 3), nullable=True)
    weekly_hosp_admissions: Mapped[Optional[float]] = mapped_column(Numeric(12, 3), nullable=True)
    weekly_hosp_admissions_per_million: Mapped[Optional[float]] = mapped_column(Numeric(10, 3), nullable=True)

    etl_run_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    loaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    country: Mapped["Country"] = relationship("Country", back_populates="hospitalizations")

    def __repr__(self) -> str:
        return f"<Hospitalization iso={self.iso_code!r} date={self.date} icu={self.icu_patients}>"
