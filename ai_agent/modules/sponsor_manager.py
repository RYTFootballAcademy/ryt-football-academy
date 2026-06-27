from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Sponsor:
    id: int
    name: str
    company: str
    contact_email: str
    contribution_amount: Optional[float] = None
    status: str = "Prospect"  # Prospect, Active, Inactive

class SponsorManager:
    def __init__(self):
        self.sponsors: List[Sponsor] = []

    def add_sponsor(self, sponsor: Sponsor):
        self.sponsors.append(sponsor)
        return sponsor

    def list_sponsors(self):
        return self.sponsors

    def find_sponsor(self, sponsor_id: int) -> Optional[Sponsor]:
        for s in self.sponsors:
            if s.id == sponsor_id:
                return s
        return None

    def update_status(self, sponsor_id: int, new_status: str):
        sponsor = self.find_sponsor(sponsor_id)
        if sponsor:
            sponsor.status = new_status
            return sponsor
        return None
