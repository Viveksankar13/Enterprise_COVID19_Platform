"""
User, Role, and Permission ORM models — maps to `users`, `roles`, `permissions`.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer, SmallInteger,
    String, Text, UniqueConstraint, func, text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Role(Base):
    """Application role for RBAC. Examples: admin, analyst, viewer, api_user."""

    __tablename__ = "roles"

    role_id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("TRUE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="role")
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission", back_populates="role", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Role id={self.role_id} name={self.name!r}>"


class Permission(Base):
    """Fine-grained permission mapping a role to a (resource, action) pair."""

    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "resource", "action", name="uq_permissions_role_resource_action"),
    )

    permission_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("roles.role_id", ondelete="CASCADE"), nullable=False, index=True
    )
    resource: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    role: Mapped["Role"] = relationship("Role", back_populates="permissions")

    def __repr__(self) -> str:
        return f"<Permission role={self.role_id} {self.resource}:{self.action}>"


class User(Base):
    """Platform user with bcrypt-hashed password and role assignment."""

    __tablename__ = "users"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    # CITEXT in Postgres handled via String — comparison is case-insensitive at DB level
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("roles.role_id", ondelete="RESTRICT"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("TRUE")
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("FALSE")
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    role: Mapped["Role"] = relationship("Role", back_populates="users")

    def __repr__(self) -> str:
        return f"<User id={self.user_id} email={self.email!r} role={self.role_id}>"
