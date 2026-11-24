"""
SQLAlchemy 2.x declarative base configuration.
All ORM models inherit from this Base.
"""

from sqlalchemy.orm import DeclarativeBase, MappedColumn
from sqlalchemy import MetaData

# ─────────────────────────────────────────────────────────────────────────────
# Naming conventions for auto-generated constraint names.
# These mirror what Alembic will generate so migration diffs stay clean.
# ─────────────────────────────────────────────────────────────────────────────
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Shared declarative base for all ORM models.

    All models inherit this class, giving them:
    - Consistent constraint naming via NAMING_CONVENTION
    - Shared MetaData instance (required for Alembic autogenerate)
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
