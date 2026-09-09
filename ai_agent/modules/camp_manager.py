"""Camp helper backed by the canonical CRM Camp model."""

from sqlalchemy.orm import Session

from ai_agent.crm.models import Camp


class CampManager:
    def add_camp(self, db: Session, name: str, start_date, end_date, capacity: int):
        start_value = start_date.isoformat() if hasattr(start_date, "isoformat") else str(start_date)
        end_value = end_date.isoformat() if hasattr(end_date, "isoformat") else str(end_date)
        camp = Camp(
            name=name,
            start_date=start_value,
            end_date=end_value,
            capacity=capacity,
        )
        db.add(camp)
        db.commit()
        db.refresh(camp)
        return camp

    def list_camps(self, db: Session):
        return db.query(Camp).order_by(Camp.id.desc()).all()
