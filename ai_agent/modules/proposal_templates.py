from typing import Dict

class ProposalTemplates:
    def get_template(self, sponsor_name: str, academy_name: str = "RYT Football Academy") -> Dict:
        return {
            "title": f"Sponsorship Proposal for {sponsor_name}",
            "sections": [
                {"header": "Introduction", "content": f"Welcome {sponsor_name}, we value your partnership."},
                {"header": "Academy Overview", "content": f"{academy_name} is committed to youth development."},
                {"header": "Funding Impact", "content": "Your support will directly empower players and community."},
                {"header": "Next Steps", "content": "We look forward to meeting and finalizing this partnership."}
            ]
        }
