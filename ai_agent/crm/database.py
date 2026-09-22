"""Compatibility exports for the legacy CRM database module.

The project now uses a single database configuration in
``ai_agent.modules.database``. Importing from this module remains supported so
older code does not silently create or write to a second ``academy_crm.db``.
"""

from ai_agent.modules.database import Base, SessionLocal, engine, get_db, init_db
from ai_agent.crm.models import Fee, Parent, Player, Tournament, Trial

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "Player",
    "Parent",
    "Fee",
    "Trial",
    "Tournament",
]
