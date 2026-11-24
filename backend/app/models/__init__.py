"""
models package — exposes all ORM models for import convenience.

Import from here to avoid circular import issues:
    from app.models import Country, DailyMetric, User
"""

from app.models.calendar import Calendar
from app.models.country import Country
from app.models.daily_metric import DailyMetric
from app.models.demographic import Demographic
from app.models.etl_log import AuditLog, ETLLog
from app.models.hospitalization import Hospitalization
from app.models.testing import Testing
from app.models.user import Permission, Role, User
from app.models.vaccination import Vaccination

__all__ = [
    "Calendar",
    "Country",
    "DailyMetric",
    "Demographic",
    "ETLLog",
    "AuditLog",
    "Hospitalization",
    "Testing",
    "Role",
    "Permission",
    "User",
    "Vaccination",
]
