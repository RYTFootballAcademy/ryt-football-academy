from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from ai_agent.modules.database import Base
import datetime

class FollowUp(Base):
    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"))
    message = Column(String)
    date_sent = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="Pending")

class SponsorFollowUp:
    def schedule_followup(self, db: Session, sponsor_id: int, message: str):
        followup = FollowUp(sponsor_id=sponsor_id, message=message)
        db.add(followup)
        db.commit()
        db.refresh(followup)
        return followup

    def list_followups(self, db: Session):
        return db.query(FollowUp).all()
