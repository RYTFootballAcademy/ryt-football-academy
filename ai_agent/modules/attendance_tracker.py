from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from ai_agent.modules.database import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    date = Column(Date)
    session_type = Column(String)  # Training / Match
    status = Column(String)        # Present / Absent

class AttendanceTracker:
    def record_attendance(self, db: Session, player_id: int, date, session_type: str, status: str):
        record = Attendance(player_id=player_id, date=date, session_type=session_type, status=status)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_player_attendance(self, db: Session, player_id: int):
        return db.query(Attendance).filter(Attendance.player_id == player_id).all()
