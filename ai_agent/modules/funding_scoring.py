from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float
from ai_agent.modules.database import Base

class FundingScore(Base):
    __tablename__ = "funding_scores"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_name = Column(String)
    score = Column(Float)  # AI/logic-based score

class FundingScoring:
    def add_score(self, db: Session, opportunity_name: str, score: float):
        fs = FundingScore(opportunity_name=opportunity_name, score=score)
        db.add(fs)
        db.commit()
        db.refresh(fs)
        return fs

    def list_scores(self, db: Session):
        return db.query(FundingScore).all()
