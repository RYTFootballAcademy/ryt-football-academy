from sqlalchemy.orm import Session
from ai_agent.crm.models import Player, Fee, Sponsor

class AnalyticsDashboard:
    def player_count(self, db: Session):
        return db.query(Player).count()

    def total_fees_collected(self, db: Session):
        return sum(f.amount for f in db.query(Fee).filter(Fee.status == "Paid").all())

    def sponsor_contributions(self, db: Session):
        return sum(s.contribution_amount for s in db.query(Sponsor).filter(Sponsor.status == "Active").all())



