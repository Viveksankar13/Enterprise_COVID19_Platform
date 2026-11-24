"""
Country ORM model — maps to the `countries` table.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.daily_metric import DailyMetric
    from app.models.vaccination import Vaccination
    from app.models.testing import Testing
    from app.models.hospitalization import Hospitalization
    from app.models.demographic import Demographic


class Country(Base):
    """
    Master dimension table for all geographic entities in the OWID dataset.

    Holds ISO 3166-1 alpha-3 codes plus OWID aggregate codes (OWID_WRL, etc.).
    One country row is the parent for all fact table rows.
    """

    __tablename__ = "countries"

    # ── Primary Key ──────────────────────────────────────────────────────────
    iso_code: Mapped[str] = mapped_column(
        String(8),
        primary_key=True,
        comment="ISO 3166-1 alpha-3 code or OWID custom aggregate code.",
    )

    # ── Core Attributes ──────────────────────────────────────────────────────
    continent: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Continent name. NULL for global aggregates.",
    )
    location: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Human-readable country or region name.",
    )

    # ── Classification ───────────────────────────────────────────────────────
    income_group: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="World Bank income classification.",
    )
    who_region: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="WHO region name.",
    )
    world_bank_region: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # ── Flags ────────────────────────────────────────────────────────────────
    is_aggregate: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("FALSE"),
        comment="TRUE for OWID aggregate rows (World, Europe, High income, etc.).",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("TRUE"),
    )

    # ── Metadata ─────────────────────────────────────────────────────────────
    data_source: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default="OWID",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ── Relationships ────────────────────────────────────────────────────────
    demographic: Mapped[Optional["Demographic"]] = relationship(
        "Demographic",
        back_populates="country",
        uselist=False,
        lazy="select",
        cascade="all, delete-orphan",
    )
    daily_metrics: Mapped[List["DailyMetric"]] = relationship(
        "DailyMetric",
        back_populates="country",
        lazy="dynamic",
    )
    vaccinations: Mapped[List["Vaccination"]] = relationship(
        "Vaccination",
        back_populates="country",
        lazy="dynamic",
    )
    testing: Mapped[List["Testing"]] = relationship(
        "Testing",
        back_populates="country",
        lazy="dynamic",
    )
    hospitalizations: Mapped[List["Hospitalization"]] = relationship(
        "Hospitalization",
        back_populates="country",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<Country iso={self.iso_code!r} location={self.location!r}>"
