"""
DailyMetric ORM model — maps to the `daily_metrics` table.
Core epidemiological fact table: cases, deaths, stringency, reproduction rate.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.country import Country


class DailyMetric(Base):
    """
    Core epidemiological fact table.

    Composite primary key: (iso_code, date).
    One row per country per day. Source: Our World in Data.
    """

    __tablename__ = "daily_metrics"
    __table_args__ = (
        CheckConstraint("total_cases IS NULL OR total_cases >= 0",   name="total_cases_nonneg"),
        CheckConstraint("total_deaths IS NULL OR total_deaths >= 0", name="total_deaths_nonneg"),
        CheckConstraint(
            "stringency_index IS NULL OR (stringency_index BETWEEN 0 AND 100)",
            name="stringency_range",
        ),
        CheckConstraint(
            "reproduction_rate IS NULL OR (reproduction_rate BETWEEN 0 AND 50)",
            name="reproduction_rate_range",
        ),
    )

    # ── Composite Primary Key ─────────────────────────────────────────────────
    iso_code: Mapped[str] = mapped_column(
        String(8),
        ForeignKey("countries.iso_code", ondelete="RESTRICT"),
        primary_key=True,
        nullable=False,
    )
    date: Mapped[date] = mapped_column(
        Date,
        ForeignKey("calendar.date_value", ondelete="RESTRICT"),
        primary_key=True,
        nullable=False,
        index=True,
    )

    # ── Case Metrics ─────────────────────────────────────────────────────────
    new_cases: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    new_cases_smoothed: Mapped[Optional[float]] = mapped_column(Numeric(14, 3), nullable=True)
    total_cases: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    new_cases_per_million: Mapped[Optional[float]] = mapped_column(Numeric(14, 3), nullable=True)
    new_cases_smoothed_per_million: Mapped[Optional[float]] = mapped_column(Numeric(14, 3), nullable=True)
    total_cases_per_million: Mapped[Optional[float]] = mapped_column(Numeric(14, 3), nullable=True)

    # ── Death Metrics ─────────────────────────────────────────────────────────
    new_deaths: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    new_deaths_smoothed: Mapped[Optional[float]] = mapped_column(Numeric(12, 3), nullable=True)
    total_deaths: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    new_deaths_per_million: Mapped[Optional[float]] = mapped_column(Numeric(12, 3), nullable=True)
    new_deaths_smoothed_per_million: Mapped[Optional[float]] = mapped_column(Numeric(12, 3), nullable=True)
    total_deaths_per_million: Mapped[Optional[float]] = mapped_column(Numeric(12, 3), nullable=True)

    # ── Epidemiological ───────────────────────────────────────────────────────
    reproduction_rate: Mapped[Optional[float]] = mapped_column(Numeric(6, 3), nullable=True)

    # ── Policy ────────────────────────────────────────────────────────────────
    stringency_index: Mapped[Optional[float]] = mapped_column(Numeric(6, 3), nullable=True)

    # ── Audit ─────────────────────────────────────────────────────────────────
    etl_run_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    loaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    country: Mapped["Country"] = relationship("Country", back_populates="daily_metrics")

    def __repr__(self) -> str:
        return f"<DailyMetric iso={self.iso_code!r} date={self.date} cases={self.new_cases}>"

    @property
    def case_fatality_rate(self) -> Optional[float]:
        """Case Fatality Rate as a percentage (total_deaths / total_cases * 100)."""
        if not self.total_cases or self.total_cases == 0:
            return None
        return round((self.total_deaths or 0) / self.total_cases * 100, 4)
