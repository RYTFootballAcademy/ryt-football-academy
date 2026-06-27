# ai_agent/modules/proposal_generator.py
from typing import Dict

class ProposalGenerator:
    def __init__(self):
        pass

    def generate_proposal(self, sponsor_name: str, contribution_amount: float, academy_name: str = "RYT Football Academy") -> Dict:
        """Generate a simple sponsor-ready proposal document structure."""
        proposal = {
            "title": f"Sponsorship Proposal for {sponsor_name}",
            "academy": academy_name,
            "sponsor": sponsor_name,
            "contribution_amount": contribution_amount,
            "content": f"""
Dear {sponsor_name},

We are excited to present this sponsorship proposal on behalf of {academy_name}.
Your support of {contribution_amount} will directly contribute to player development,
academy growth, and community impact.

We look forward to building a strong partnership with you.

Sincerely,
{academy_name} Management
"""
        }
        return proposal
