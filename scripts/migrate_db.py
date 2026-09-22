"""Run the non-destructive FAOS SQLite schema upgrade manually.

This file can be launched either as ``python scripts/migrate_db.py`` on Windows
or ``python -m scripts.migrate_db`` on any platform.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai_agent.modules.database import init_db  # noqa: E402


if __name__ == "__main__":
    applied = init_db()
    if applied:
        print("Applied additive migrations:")
        for migration in applied:
            print(f" - {migration}")
    else:
        print("Database schema is already current.")
