"""Seed a fresh FAOS database with the RYT Sports Academy foundation.

This file can be launched either as ``python scripts/seed_ryt.py`` on Windows
or ``python -m scripts.seed_ryt`` on any platform.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai_agent.faos.models import Organization, Team  # noqa: E402
from ai_agent.modules.database import SessionLocal, init_db  # noqa: E402

ACADEMY_NAME = "Roshunville Young Tigers Sports Academy"
AGE_GROUPS = ["U9", "U10", "U13", "U15", "U17", "U19"]


def seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        organization = db.query(Organization).filter(Organization.name == ACADEMY_NAME).first()
        if organization is None:
            organization = Organization(
                name=ACADEMY_NAME,
                established="2022",
                town="Schweizer-Reneke",
                province="North West",
                country="South Africa",
                status="Active",
            )
            db.add(organization)
            db.flush()
            print(f"Created organization: {ACADEMY_NAME}")
        else:
            print(f"Organization already exists: {ACADEMY_NAME}")

        existing = {
            team.age_group
            for team in db.query(Team).filter(Team.organization_id == organization.id).all()
        }
        for age_group in AGE_GROUPS:
            if age_group in existing:
                continue
            db.add(
                Team(
                    organization_id=organization.id,
                    name=f"RYT {age_group}",
                    age_group=age_group,
                    training_days="Monday, Tuesday, Thursday",
                    venue="Roshunville Sports Grounds",
                )
            )
            print(f"Created team: RYT {age_group}")

        db.commit()
        print("RYT seed complete.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
