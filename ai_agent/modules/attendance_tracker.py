"""Attendance helper backed by the canonical CRM Attendance model."""

from sqlalchemy.orm import Session

from ai_agent.crm.models import Attendance


class AttendanceTracker:
    def record_attendance(
        self,
        db: Session,
        player_id: int,
        date,
        session_type: str,
        status: str,
    ):
        date_value = date.isoformat() if hasattr(date, "isoformat") else str(date)
        record = Attendance(
            player_id=player_id,
            date=date_value,
            session_type=session_type,
            status=status,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_player_attendance(self, db: Session, player_id: int):
        return (
            db.query(Attendance)
            .filter(Attendance.player_id == player_id)
            .order_by(Attendance.id.desc())
            .all()
        )
