"""Deterministic decision router for the RYT Football Academy FAOS.

This is the local/offline reasoning layer. It classifies academy requests and
returns useful operational next actions and relevant FAOS endpoints. A future
LLM provider can sit behind the same API without making the core system depend
on an external service.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Task:
    """An incoming academy request with optional structured context."""

    user_input: str
    context: Dict[str, Any] = field(default_factory=dict)


class RYTAI_Agent:
    """Rule-based FAOS copilot and module router."""

    ROUTES = {
        "sponsor": ["sponsor", "funding", "donation", "donor", "grant", "proposal"],
        "npo": ["npo", "director", "member", "compliance", "dsd", "annual return", "constitution", "policy"],
        "coaching": ["training", "coach", "practice", "drill", "camp", "match", "player", "trial", "fitness", "injury"],
        "finance": ["fee", "budget", "expense", "income", "bank", "payment", "money", "finance"],
        "commerce": ["shop", "merch", "shirt", "product", "stock", "order", "customer"],
        "communication": ["whatsapp", "message", "parent", "announcement", "reminder"],
        "legal": ["contract", "legal", "agreement", "law", "resolution"],
    }

    def route_task(self, task: Task) -> Dict[str, Any]:
        text = task.user_input.strip().lower()
        if not text:
            return {
                "module": "unknown",
                "action": "request_input",
                "message": "Enter an academy task or question to route it through FAOS.",
                "recommended_actions": [],
            }

        scores = {
            module: sum(keyword in text for keyword in keywords)
            for module, keywords in self.ROUTES.items()
        }
        module = max(scores, key=scores.get)
        if scores[module] == 0:
            return self.handle_general(task)

        handler = getattr(self, f"handle_{module}")
        result = handler(task)
        result["matched_module"] = module
        result["confidence"] = round(min(1.0, 0.55 + 0.12 * scores[module]), 2)
        return result

    @staticmethod
    def _result(module: str, action: str, message: str, actions: list[str], endpoints: list[str]):
        return {
            "module": module,
            "action": action,
            "message": message,
            "recommended_actions": actions,
            "relevant_endpoints": endpoints,
        }

    def handle_sponsor(self, task: Task) -> Dict[str, Any]:
        return self._result(
            "sponsor",
            "build_pipeline",
            "Treat this as a sponsorship/funding pipeline task: record the lead or opportunity, prepare a tailored value proposition, assign a next follow-up, and track the outcome.",
            [
                "Create or update the sponsor/funding record.",
                "Define the academy need, requested value and sponsor benefit.",
                "Prepare outreach/proposal material for human approval.",
                "Record follow-up date, response and status.",
            ],
            ["/crm/sponsors", "/crm/funding", "/crm/proposals", "/faos/follow_ups"],
        )

    def handle_npo(self, task: Task) -> Dict[str, Any]:
        return self._result(
            "npo",
            "governance_workflow",
            "Treat this as a governance/compliance task and preserve an auditable record of the responsible person, deadline, evidence and completion status.",
            [
                "Record the compliance task and due date.",
                "Link the relevant meeting, resolution, policy or annual return.",
                "Store supporting evidence outside the database and record its reference.",
                "Mark completion only after the responsible person verifies filing or adoption.",
            ],
            ["/crm/compliance", "/faos/directors", "/faos/governance_meetings", "/faos/annual_returns", "/faos/policies"],
        )

    def handle_coaching(self, task: Task) -> Dict[str, Any]:
        return self._result(
            "coaching",
            "football_operations",
            "Treat this as a player-development or football-operations task and connect the activity to the relevant team/player so progress can be measured over time.",
            [
                "Identify the team/player and objective.",
                "Record the session, match, trial, fitness test or development report.",
                "Capture attendance and measurable outcomes.",
                "Review trends before the next development decision.",
            ],
            ["/crm/players", "/crm/attendance", "/crm/trials", "/faos/training_sessions", "/faos/matches", "/faos/development_reports"],
        )

    def handle_finance(self, task: Task) -> Dict[str, Any]:
        return self._result(
            "finance",
            "financial_control",
            "Treat this as a finance-control task: record the transaction or obligation, classify it, reconcile it and keep academy/NPO money traceable.",
            [
                "Record the fee, payment, income or expense.",
                "Use a category/reference that can be reconciled to evidence.",
                "Review outstanding fees and budget variance.",
                "Keep bank and cash records separate from personal finances.",
            ],
            ["/crm/fees", "/faos/player_payments", "/faos/expenses", "/faos/income", "/faos/budgets", "/faos/bank_accounts"],
        )

    def handle_commerce(self, task: Task) -> Dict[str, Any]:
        return self._result(
            "commerce",
            "commerce_workflow",
            "Treat this as a stock/order workflow: maintain a product record, customer/order trail, payment reference and current stock balance.",
            [
                "Create/update the product and stock quantity.",
                "Record the customer and order.",
                "Record each order item and payment.",
                "Reconcile stock after fulfilment or cancellation.",
            ],
            ["/crm/products", "/faos/customers", "/faos/orders", "/faos/order_items", "/faos/order_payments"],
        )

    def handle_communication(self, task: Task) -> Dict[str, Any]:
        return self._result(
            "communication",
            "communication_queue",
            "Prepare the communication, verify the recipient/audience and queue it. Real WhatsApp delivery remains disabled until an approved provider is connected.",
            [
                "Confirm recipient details and purpose.",
                "Review the message before external delivery.",
                "Queue it through the communication endpoint.",
                "Connect Meta/Twilio only when credentials and consent processes are ready.",
            ],
            ["/whatsapp/send", "/whatsapp/queue", "/crm/messages", "/crm/parents"],
        )

    def handle_legal(self, task: Task) -> Dict[str, Any]:
        return self._result(
            "legal",
            "document_support",
            "FAOS can organize facts, drafts, agreements and resolutions, but legal documents should be reviewed by an appropriately qualified person before signature or filing.",
            [
                "Record the parties, purpose, dates and approval authority.",
                "Prepare a draft or checklist without representing it as legal advice.",
                "Link the relevant board resolution/policy where applicable.",
                "Obtain appropriate review before execution.",
            ],
            ["/faos/resolutions", "/faos/policies", "/faos/sponsorship_agreements", "/faos/constitution_versions"],
        )

    def handle_general(self, task: Task) -> Dict[str, Any]:
        return self._result(
            "general",
            "academy_admin",
            "The request does not map strongly to one specialist workflow. Start from the academy dashboard or resource registry and capture the underlying record before automating further actions.",
            [
                "Check the CRM summary for the current operating picture.",
                "Identify which FAOS resource owns the information.",
                "Create/update that record before adding automation.",
            ],
            ["/crm/summary", "/faos/resources", "/docs"],
        )
