"""
RYT Football Academy - Core AI Agent
-----------------------------------
This is the central routing engine for the RYT Football Academy AI system.
It directs tasks to the correct module (sponsors, NPO, coaching, commerce, legal).

NOTE:
This is a scaffold version. Modules will be expanded in later steps.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Task:
    """Represents an incoming request to the AI Agent."""
    user_input: str
    context: Dict[str, Any] = None


class RYTAI_Agent:
    """Core decision-making engine for RYT Football Academy."""

    def __init__(self):
        self.modules = {
            "sponsor": self.handle_sponsors,
            "npo": self.handle_npo,
            "coaching": self.handle_coaching,
            "commerce": self.handle_commerce,
            "legal": self.handle_legal,
        }

    def route_task(self, task: Task) -> Dict[str, Any]:
        """
        Main routing function.
        Determines which module should handle the request.
        """
        text = task.user_input.lower()

        # Simple rule-based routing (will later be replaced with AI model)
        if any(k in text for k in ["sponsor", "funding", "donation", "donor"]):
            return self.modules["sponsor"](task)

        if any(k in text for k in ["npo", "director", "member", "compliance", "dsd"]):
            return self.modules["npo"](task)

        if any(k in text for k in ["training", "coach", "practice", "drill", "camp"]):
            return self.modules["coaching"](task)

        if any(k in text for k in ["shop", "merch", "shirt", "payment", "order"]):
            return self.modules["commerce"](task)

        if any(k in text for k in ["contract", "legal", "agreement", "law"]):
            return self.modules["legal"](task)

        return {
            "module": "unknown",
            "response": "Request not matched. Please refine input or add new rule."
        }

    # ---------------- MODULE HANDLERS ----------------

    def handle_sponsors(self, task: Task) -> Dict[str, Any]:
        return {
            "module": "sponsor",
            "action": "generate_outreach",
            "message": "Sponsor module triggered (placeholder)."
        }

    def handle_npo(self, task: Task) -> Dict[str, Any]:
        return {
            "module": "npo",
            "action": "compliance_check",
            "message": "NPO module triggered (placeholder)."
        }

    def handle_coaching(self, task: Task) -> Dict[str, Any]:
        return {
            "module": "coaching",
            "action": "training_plan",
            "message": "Coaching module triggered (placeholder)."
        }

    def handle_commerce(self, task: Task) -> Dict[str, Any]:
        return {
            "module": "commerce",
            "action": "order_management",
            "message": "Commerce module triggered (placeholder)."
        }

    def handle_legal(self, task: Task) -> Dict[str, Any]:
        return {
            "module": "legal",
            "action": "draft_support",
            "message": "Legal support module triggered (placeholder - not legal advice)."
        }


# Example usage
if __name__ == "__main__":
    agent = RYTAI_Agent()

    sample_task = Task(user_input="We need sponsors for new kits")
    result = agent.route_task(sample_task)

    print(result)
