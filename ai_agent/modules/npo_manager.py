"""
RYT Football Academy - NPO Manager Module
-----------------------------------------
Handles nonprofit organisation (NPO) structure tracking, compliance monitoring,
and support for Department of Social Development (DSD) funding readiness.

This is a scaffold module for future expansion.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class Director:
    name: str
    id_number: Optional[str] = None
    role: Optional[str] = None
    active: bool = True


@dataclass
class Member:
    name: str
    joined_date: datetime = field(default_factory=datetime.utcnow)
    active: bool = True


class NPOManager:
    """Manages NPO compliance, directors, members, and funding readiness."""

    def __init__(self):
        self.directors: List[Director] = []
        self.members: List[Member] = []
        self.documents: Dict[str, Any] = {}
        self.compliance_flags: List[str] = []

    # ---------------- DIRECTORS ----------------

    def add_director(self, name: str, id_number: str = None, role: str = None):
        self.directors.append(Director(name, id_number, role))
        return {"status": "success", "message": f"Director {name} added"}

    def deactivate_director(self, name: str):
        for d in self.directors:
            if d.name == name:
                d.active = False
                return {"status": "updated", "message": f"Director {name} deactivated"}
        return {"status": "not_found"}

    def list_active_directors(self):
        return [d for d in self.directors if d.active]

    # ---------------- MEMBERS ----------------

    def add_member(self, name: str):
        self.members.append(Member(name))
        return {"status": "success", "message": f"Member {name} added"}

    def deactivate_member(self, name: str):
        for m in self.members:
            if m.name == name:
                m.active = False
                return {"status": "updated", "message": f"Member {name} deactivated"}
        return {"status": "not_found"}

    def list_active_members(self):
        return [m for m in self.members if m.active]

    # ---------------- COMPLIANCE ----------------

    def add_document(self, doc_name: str, content: str):
        self.documents[doc_name] = {
            "content": content,
            "updated_at": datetime.utcnow().isoformat()
        }
        return {"status": "saved", "document": doc_name}

    def check_compliance(self):
        """Basic compliance checks for funding readiness."""
        self.compliance_flags.clear()

        if len(self.list_active_directors()) < 3:
            self.compliance_flags.append("Less than 3 active directors")

        if len(self.list_active_members()) < 5:
            self.compliance_flags.append("Low active membership count")

        if "constitution" not in self.documents:
            self.compliance_flags.append("Missing constitution document")

        return {
            "compliant": len(self.compliance_flags) == 0,
            "flags": self.compliance_flags
        }

    # ---------------- FUNDING READINESS ----------------

    def funding_readiness_score(self):
        score = 0

        if len(self.list_active_directors()) >= 3:
            score += 30
        if len(self.list_active_members()) >= 10:
            score += 30
        if "constitution" in self.documents:
            score += 20
        if "financial_report" in self.documents:
            score += 20

        return {
            "score": score,
            "status": "ready" if score >= 70 else "not_ready"
        }


# Example usage
if __name__ == "__main__":
    npo = NPOManager()
    npo.add_director("Example Director", "0000000000000", "Chairperson")
    npo.add_member("Example Member")
    print(npo.check_compliance())
