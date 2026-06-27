from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from ai_agent.modules.database import Base
import datetime

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parents.id"))
    content = Column(String)
    date_sent = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="Sent")

class ParentHub:
    def send_message(self, db: Session, parent_id: int, content: str):
        msg = Message(parent_id=parent_id, content=content)
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    def get_messages(self, db: Session, parent_id: int):
        return db.query(Message).filter(Message.parent_id == parent_id).all()
