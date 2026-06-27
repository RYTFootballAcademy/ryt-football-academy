from sqlalchemy.orm import Session
from ai_agent.crm.models import Fee

class FeeManager:
    def add_fee(self, db: Session, player_id: int, amount: float, status: str = "Pending"):
        fee = Fee(player_id=player_id, amount=amount, status=status)
        db.add(fee)
        db.commit()
        db.refresh(fee)
        return fee

    def list_fees(self, db: Session):
        return db.query(Fee).all()

    def outstanding_fees(self, db: Session):
        return db.query(Fee).filter(Fee.status == "Pending").all()
