"""Coach helper backed by the canonical CRM Coach model."""

from sqlalchemy.orm import Session

from ai_agent.crm.models import Coach


class CoachManager:
    def add_coach(
        self,
        db: Session,
        name: str,
        role: str,
        phone: str,
        assigned_team: str = None,
    ):
        coach = Coach(
            name=name,
            role=role,
            phone=phone,
            assigned_team=assigned_team,
        )
        db.add(coach)
        db.commit()
        db.refresh(coach)
        return coach

    def list_coaches(self, db: Session):
        return db.query(Coach).order_by(Coach.id.desc()).all()

    def assign_team(self, db: Session, coach_id: int, team: str):
        coach = db.get(Coach, coach_id)
        if coach:
            coach.assigned_team = team
            db.commit()
            db.refresh(coach)
        return coach
