# ai_agent/modules/camp_manager.py
from sqlalchemy import Column, Integer, String, Date
from ai_agent.modules.database import Base
from sqlalchemy.orm import Session

class Camp(Base):
    __tablename__ = "camps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    capacity = Column(Integer)

class CampManager:
    def add_camp(self, db: Session, name: str, start_date, end_date, capacity: int):
        camp = Camp(name=name, start_date=start_date, end_date=end_date, capacity=capacity)
        db.add(camp)
        db.commit()
        db.refresh(camp)
        return camp

    def list_camps(self, db: Session):
        return db.query(Camp).all()
