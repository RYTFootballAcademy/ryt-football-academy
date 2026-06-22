"""
RYT Football Academy - Sponsor Engine Module
--------------------------------------------
Handles sponsor discovery, outreach generation, and sponsor pipeline tracking.
This module is designed to support structured sponsorship acquisition workflows
(not guaranteed funding or results).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class SponsorLead:
    name: str
    industry: Optional[str] = None
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    status: str = "new"  # new, contacted, interested, rejected, confirmed
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class SponsorEngine:
    """Manages sponsor outreach pipeline and tracking."""

    def __init__(self):
        self.leads: List[SponsorLead] = []
        self.outreach_templates: Dict[str, str] = {
            "email": "Dear {name}, we invite you to support RYT Football Academy...",
            "whatsapp": "Hi {name}, RYT Football Academy is looking for sponsors..."
        }

    # ---------------- LEAD MANAGEMENT ----------------

    def add_lead(self, name: str, industry: str = None, email: str = None, phone: str = None):
        lead = SponsorLead(
            name=name,
            industry=industry,
            contact_email=email,
            phone=phone
        )
        self.leads.append(lead)
        return {"status": "success", "message": f"Lead {name} added"}

    def update_status(self, name: str, status: str):
        for lead in self.leads:
            if lead.name == name:
                lead.status = status
                return {"status": "updated", "lead": name, "new_status": status}
        return {"status": "not_found"}

    def list_leads(self, status: str = None):
        if status:
            return [l for l in self.leads if l.status == status]
        return self.leads

    # ---------------- OUTREACH GENERATION ----------------

    def generate_email(self, name: str, sponsor_name: str):
        return self.outreach_templates["email"].format(name=sponsor_name)

    def generate_whatsapp_message(self, sponsor_name: str):
        return self.outreach_templates["whatsapp"].format(name=sponsor_name)

    # ---------------- PIPELINE INSIGHTS ----------------

    def pipeline_summary(self):
        summary = {
            "new": 0,
            "contacted": 0,
            "interested": 0,
            "rejected": 0,
            "confirmed": 0,
        }

        for lead in self.leads:
            if lead.status in summary:
                summary[lead.status] += 1

        return {
            "total_leads": len(self.leads),
            "pipeline": summary
        }


# Example usage
if __name__ == "__main__":
    engine = SponsorEngine()
    engine.add_lead("Local Bakery", "Food", "contact@bakery.co.za")
    print(engine.pipeline_summary())
