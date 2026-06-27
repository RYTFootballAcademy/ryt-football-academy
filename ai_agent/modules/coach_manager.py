from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
from ai_agent.modules.database import Base

class Coach(Base):
    __tablename__ = "coaches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)
    phone = Column(String)
    assigned_team = Column(String)

class CoachManager:
    def add_coach(self, db: Session, name: str, role: str, phone: str, assigned_team: str = None):
        coach = Coach(name=name, role=role, phone=phone, assigned_team=assigned_team)
        db.add(coach)
        db.commit()
        db.refresh(coach)
        return coach

    def list_coaches(self, db: Session):
        return db.query(Coach).all()

    def assign_team(self, db: Session, coach_id: int, team: str):
        coach = db.query(Coach).filter(Coach.id == coach_id).first()
        if coach:
            coach.assigned_team = team
            db.commit()
            db.refresh(coach)
        return coach


