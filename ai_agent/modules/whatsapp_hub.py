"""
RYT Football Academy - WhatsApp Communication Hub
--------------------------------------------------
Queues messaging workflows for parents, players, sponsors, and academy staff.

Real delivery requires a configured WhatsApp Business API/Twilio integration;
this module deliberately queues messages until such a provider is connected.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List


@dataclass
class WhatsAppMessage:
    recipient: str
    message: str
    message_type: str = "text"
    status: str = "queued"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class WhatsAppHub:
    """Central communication queue for RYT Football Academy."""

    def __init__(self):
        self.message_queue: List[WhatsAppMessage] = []
        self.templates: Dict[str, str] = {
            "fee_reminder": "Dear parent, kindly be reminded of your monthly academy fee payment.",
            "match_update": "Match update: {details}",
            "training_schedule": "Training schedule update: {schedule}",
            "general_announcement": "RYT Football Academy announcement: {message}",
        }

    def send_message(self, recipient: str, message: str, message_type: str = "text"):
        msg = WhatsAppMessage(recipient=recipient, message=message, message_type=message_type)
        self.message_queue.append(msg)
        return {
            "status": msg.status,
            "recipient": msg.recipient,
            "message": msg.message,
            "message_type": msg.message_type,
            "timestamp": msg.timestamp.isoformat(),
        }

    def send_bulk(self, recipients: List[str], message: str):
        for recipient in recipients:
            self.send_message(recipient, message)
        return {"status": "bulk_queued", "count": len(recipients)}

    def send_fee_reminder(self, parent_contact: str):
        return self.send_message(parent_contact, self.templates["fee_reminder"])

    def send_match_update(self, recipients: List[str], details: str):
        return self.send_bulk(recipients, self.templates["match_update"].format(details=details))

    def send_training_schedule(self, recipients: List[str], schedule: str):
        return self.send_bulk(
            recipients,
            self.templates["training_schedule"].format(schedule=schedule),
        )

    def send_announcement(self, recipients: List[str], message: str):
        return self.send_bulk(
            recipients,
            self.templates["general_announcement"].format(message=message),
        )

    def queue_status(self):
        return {
            "total_messages": len(self.message_queue),
            "queued": sum(message.status == "queued" for message in self.message_queue),
            "sent": sum(message.status == "sent" for message in self.message_queue),
            "failed": sum(message.status == "failed" for message in self.message_queue),
        }
