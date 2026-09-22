"""Parent communication helper backed by the canonical CRM Message model."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ai_agent.crm.models import Message


class ParentHub:
    def send_message(self, db: Session, parent_id: int, content: str):
        sent_at = datetime.now(timezone.utc).isoformat()
        message = Message(
            parent_id=parent_id,
            content=content,
            timestamp=sent_at,
            date_sent=sent_at,
            status="Sent",
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_messages(self, db: Session, parent_id: int):
        return (
            db.query(Message)
            .filter(Message.parent_id == parent_id)
            .order_by(Message.id.desc())
            .all()
        )
