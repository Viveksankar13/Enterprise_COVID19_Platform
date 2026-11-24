"""
ETLLog and AuditLog ORM models — operational audit tables.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import (
    BigInteger, CheckConstraint, DateTime, Enum, ForeignKey,
    Integer, Numeric, SmallInteger, String, Text, func, text,
)
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ETLLog(Base):
    """
    Audit log for every ETL pipeline execution.

    Tracks rows processed, timing, errors, and dataset checksums.
    Append-mostly — updated only while status = RUNNING.
    """

    __tablename__ = "etl_logs"
    __table_args__ = (
        CheckConstraint(
            "completed_at IS NULL OR completed_at >= started_at",
            name="dates_order",
        ),
        CheckConstraint(
            "rows_downloaded >= 0 AND rows_validated >= 0 AND "
            "rows_rejected >= 0 AND rows_inserted >= 0 AND rows_updated >= 0",
            name="row_counts_nonneg",
        ),
    )

    run_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    pipeline_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    dag_run_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="RUNNING",
        comment="RUNNING | SUCCESS | FAILED | PARTIAL | SKIPPED",
    )

    # Row statistics
    rows_downloaded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_validated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timing
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Error info
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_traceback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Dataset metadata
    dataset_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dataset_checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    dataset_row_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_date_min: Mapped[Optional[date]] = mapped_column(DateTime(timezone=False), nullable=True)
    source_date_max: Mapped[Optional[date]] = mapped_column(DateTime(timezone=False), nullable=True)
    meta_data: Mapped[Dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)

    def __repr__(self) -> str:
        return (
            f"<ETLLog run_id={self.run_id} pipeline={self.pipeline_name!r} "
            f"status={self.status} inserted={self.rows_inserted}>"
        )

    @property
    def duration_seconds(self) -> Optional[float]:
        """Compute duration if both timestamps are available."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def rejection_rate_pct(self) -> Optional[float]:
        """Percentage of rows rejected vs. downloaded."""
        if not self.rows_downloaded:
            return None
        return round(self.rows_rejected / self.rows_downloaded * 100, 2)


class AuditLog(Base):
    """
    Immutable user action audit trail.

    Every API call that modifies state or accesses sensitive data is logged here.
    Append-only — no UPDATE or DELETE operations should be performed on this table.
    """

    __tablename__ = "audit_logs"
    __table_args__ = (
        CheckConstraint(
            "response_status IS NULL OR (response_status BETWEEN 100 AND 599)",
            name="http_status_range",
        ),
    )

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    request_method: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    request_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_status: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    meta_data: Mapped[Dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    def __repr__(self) -> str:
        return f"<AuditLog log_id={self.log_id} action={self.action!r} user={self.username!r}>"
