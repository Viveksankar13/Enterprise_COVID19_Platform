"""
Testing ORM model — maps to the `testing` table.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import (
    BigInteger, CheckConstraint, Date, DateTime,
    ForeignKey, Integer, Numeric, String, func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.country import Country


class Testing(Base):
    """COVID-19 testing metrics. Composite PK: (iso_code, date)."""

    __tablename__ = "testing"
    __table_args__ = (
        CheckConstraint(
            "positive_rate IS NULL OR (positive_rate BETWEEN 0 AND 1)",
            name="positive_rate_range",
        ),
    )

    iso_code: Mapped[str] = mapped_column(
        String(8), ForeignKey("countries.iso_code"), primary_key=True
    )
    date: Mapped[date] = mapped_column(
        Date, ForeignKey("calendar.date_value"), primary_key=True, index=True
    )

    new_tests: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_tests: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    new_tests_smoothed: Mapped[Optional[float]] = mapped_column(Numeric(12, 3), nullable=True)
    total_tests_per_thousand: Mapped[Optional[float]] = mapped_column(Numeric(12, 3), nullable=True)
    new_tests_per_thousand: Mapped[Optional[float]] = mapped_column(Numeric(10, 3), nullable=True)
    new_tests_smoothed_per_thousand: Mapped[Optional[float]] = mapped_column(Numeric(10, 3), nullable=True)
    positive_rate: Mapped[Optional[float]] = mapped_column(Numeric(7, 5), nullable=True)
    tests_per_case: Mapped[Optional[float]] = mapped_column(Numeric(10, 3), nullable=True)
    tests_units: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    etl_run_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    loaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    country: Mapped["Country"] = relationship("Country", back_populates="testing")

    def __repr__(self) -> str:
        return f"<Testing iso={self.iso_code!r} date={self.date} positive_rate={self.positive_rate}>"
