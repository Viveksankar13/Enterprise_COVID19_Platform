"""
Calendar ORM model — maps to the `calendar` date dimension table.
Pre-populated for 2019-01-01 through 2030-12-31.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Calendar(Base):
    """Date dimension table for analytics grouping and time-series joins."""

    __tablename__ = "calendar"

    date_value: Mapped[date] = mapped_column(Date, primary_key=True)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    quarter: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    month_name: Mapped[str] = mapped_column(String(10), nullable=False)
    week_of_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    day_of_month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    day_name: Mapped[str] = mapped_column(String(10), nullable=False)
    is_weekend: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_leap_year: Mapped[bool] = mapped_column(Boolean, nullable=False)
    year_month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    year_quarter: Mapped[str] = mapped_column(String(7), nullable=False)

    def __repr__(self) -> str:
        return f"<Calendar date={self.date_value} year_month={self.year_month!r}>"
