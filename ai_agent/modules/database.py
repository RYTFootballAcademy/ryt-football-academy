"""Database configuration and lightweight schema management for FAOS."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///academy.db")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine: Engine = create_engine(DATABASE_URL, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides one database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope():
    """Transactional session helper for scripts and service-layer operations."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _load_models() -> None:
    """Import all mapped models before metadata operations."""
    from ai_agent.crm import models as _crm_models  # noqa: F401
    from ai_agent.faos import models as _faos_models  # noqa: F401


def migrate_additive_schema() -> list[str]:
    """Add columns that exist in SQLAlchemy metadata but are missing in SQLite.

    This deliberately performs additive migrations only. It preserves existing data
    and fixes legacy databases created by earlier versions of this project. New
    tables are created by ``Base.metadata.create_all``. For production PostgreSQL
    deployments, use a formal migration tool before destructive schema changes.
    """
    _load_models()
    Base.metadata.create_all(bind=engine)

    if engine.dialect.name != "sqlite":
        return []

    db_inspector = inspect(engine)
    table_names = set(db_inspector.get_table_names())
    quote = engine.dialect.identifier_preparer.quote
    applied: list[str] = []

    with engine.begin() as connection:
        for table in Base.metadata.sorted_tables:
            if table.name not in table_names:
                continue
            existing = {column["name"] for column in db_inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing:
                    continue
                column_type = column.type.compile(dialect=engine.dialect)
                statement = (
                    f"ALTER TABLE {quote(table.name)} "
                    f"ADD COLUMN {quote(column.name)} {column_type}"
                )
                connection.execute(text(statement))
                applied.append(f"{table.name}.{column.name}")

        # Preserve contact details from the original academy_crm Parent schema.
        if "parents" in table_names:
            parent_columns = {
                column["name"] for column in inspect(engine).get_columns("parents")
            }
            if {"contact", "phone"}.issubset(parent_columns):
                connection.execute(
                    text("UPDATE parents SET phone = contact WHERE phone IS NULL AND contact IS NOT NULL")
                )

    return applied


def init_db() -> list[str]:
    """Create missing tables and safely upgrade legacy SQLite schemas."""
    _load_models()
    Base.metadata.create_all(bind=engine)
    return migrate_additive_schema()
