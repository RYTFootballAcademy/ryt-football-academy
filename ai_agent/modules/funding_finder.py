# ai_agent/modules/funding_finder.py
from typing import List, Dict

class FundingFinder:
    def __init__(self):
        # This will hold opportunities in memory for now
        self.opportunities: List[Dict] = []

    def add_opportunity(self, category: str, name: str, description: str, contact: str):
        """Add a new funding opportunity."""
        opportunity = {
            "category": category,
            "name": name,
            "description": description,
            "contact": contact
        }
        self.opportunities.append(opportunity)
        return opportunity

    def list_opportunities(self):
        """List all tracked funding opportunities."""
        return self.opportunities

    def find_by_category(self, category: str):
        """Filter opportunities by category."""
        return [opp for opp in self.opportunities if opp["category"].lower() == category.lower()]
