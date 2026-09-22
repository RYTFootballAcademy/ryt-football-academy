"""Controlled preparation and execution of approved FAOS agent actions."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from ai_agent.core.action_models import AgentTask
from ai_agent.core.agent import RYTAI_Agent, Task
from ai_agent.crm.models import (
    Attendance,
    Coach,
    ComplianceTask,
    Fee,
    FundingOpportunity,
    Message,
    Parent,
    Player,
    Sponsor,
)
from ai_agent.faos.models import Director, GeneratedReport
from ai_agent.faos.company_models import (
    BeneficialOwnershipFiling,
    CompanyFinancialFiling,
    DirectorChangeCase,
    DSDAnnualReport,
)
from ai_agent.faos.npo_models import NPORegulatoryProfile, RegulatoryFiling


EXECUTABLE_ACTIONS = {
    "create_compliance_task",
    "update_npo_profile",
    "create_funding_opportunity",
    "prepare_parent_message",
    "generate_management_report",
    "manual_review",
    "prepare_director_change",
    "record_regulatory_filing",
    "record_beneficial_ownership",
    "record_company_financial_filing",
    "prepare_dsd_annual_report",
}

NPO_EDITABLE_FIELDS = {
    "legal_name",
    "trading_name",
    "entity_type",
    "cipc_registration_number",
    "cipc_status",
    "incorporation_date",
    "dsd_npo_number",
    "dsd_registration_date",
    "dsd_status",
    "financial_year_end",
    "sars_income_tax_number",
    "pbo_number",
    "tax_exemption_status",
    "physical_address",
    "postal_address",
    "notes",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _loads(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    loaded = json.loads(value)
    return loaded if isinstance(loaded, dict) else {}


def serialize_task(task: AgentTask) -> dict[str, Any]:
    return {
        "id": task.id,
        "organization_id": task.organization_id,
        "title": task.title,
        "module": task.module,
        "action_type": task.action_type,
        "description": task.description,
        "payload": _loads(task.payload_json),
        "priority": task.priority,
        "status": task.status,
        "requires_approval": bool(task.requires_approval),
        "created_at": task.created_at,
        "approved_at": task.approved_at,
        "approved_by": task.approved_by,
        "rejected_at": task.rejected_at,
        "rejection_reason": task.rejection_reason,
        "executed_at": task.executed_at,
        "result": _loads(task.result_json),
        "error": task.error,
    }


def create_task(
    db: Session,
    *,
    title: str,
    module: str,
    action_type: str,
    description: str | None = None,
    payload: dict[str, Any] | None = None,
    organization_id: int | None = 1,
    priority: str = "Normal",
) -> AgentTask:
    if action_type not in EXECUTABLE_ACTIONS:
        raise ValueError(f"Unsupported action_type: {action_type}")

    task = AgentTask(
        organization_id=organization_id,
        title=title.strip(),
        module=module.strip() or "general",
        action_type=action_type,
        description=description,
        payload_json=json.dumps(payload or {}, ensure_ascii=False),
        priority=priority,
        status="Awaiting Approval",
        requires_approval=True,
        created_at=utc_now(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def _title_from_instruction(instruction: str, fallback: str) -> str:
    text = instruction.strip().rstrip(".")
    match = re.search(r"\b(?:task|action)\s+to\s+(.+)$", text, flags=re.IGNORECASE)
    if match:
        text = match.group(1)
    elif re.match(r"^(create|prepare|draft|generate)\b", text, flags=re.IGNORECASE):
        text = re.sub(
            r"^(create|prepare|draft|generate)\s+(?:a|an|the)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )
    return (text[:1].upper() + text[1:])[:240] if text else fallback


def _parent_message_draft(instruction: str) -> str:
    lower = instruction.lower()
    if "emergency" in lower and "contact" in lower:
        return (
            "Dear Parent/Guardian, please update or confirm your child's current "
            "emergency contact and medical information with RYT Sports Academy. "
            "This helps us keep accurate records for player safety. Thank you."
        )
    if "training" in lower:
        return (
            "Dear Parent/Guardian, RYT Sports Academy has a training update for "
            "your attention. Please review the academy communication and contact "
            "us if you need clarification. Thank you."
        )
    return (
        "Dear Parent/Guardian, RYT Sports Academy would like to share an update "
        f"regarding: {instruction.strip()} Please contact the academy if you have "
        "any questions. Thank you."
    )


def prepare_from_instruction(
    db: Session,
    agent: RYTAI_Agent,
    instruction: str,
    *,
    organization_id: int | None = 1,
    priority: str = "Normal",
) -> AgentTask:
    instruction = instruction.strip()
    if not instruction:
        raise ValueError("Instruction cannot be empty")

    route = agent.route_task(Task(user_input=instruction))
    module = str(route.get("module") or route.get("matched_module") or "general")
    lower = instruction.lower()

    if "report" in lower or "management summary" in lower or "management report" in lower:
        return create_task(
            db,
            title=_title_from_instruction(instruction, "Generate management report"),
            module="reporting",
            action_type="generate_management_report",
            description=instruction,
            payload={},
            organization_id=organization_id,
            priority=priority,
        )

    if "parent" in lower and any(word in lower for word in ("message", "whatsapp", "communicat")):
        return create_task(
            db,
            title=_title_from_instruction(instruction, "Prepare parent message"),
            module="communication",
            action_type="prepare_parent_message",
            description=instruction,
            payload={"content": _parent_message_draft(instruction)},
            organization_id=organization_id,
            priority=priority,
        )

    if any(word in lower for word in ("compliance", "cipc", "dsd", "sars", "beneficial ownership")):
        return create_task(
            db,
            title=_title_from_instruction(instruction, "Create compliance task"),
            module="npo",
            action_type="create_compliance_task",
            description=instruction,
            payload={
                "title": _title_from_instruction(instruction, "Compliance action"),
                "description": instruction,
                "status": "Pending",
            },
            organization_id=organization_id,
            priority=priority,
        )

    if "funding" in lower or "grant" in lower:
        name = _title_from_instruction(instruction, "Funding opportunity")
        return create_task(
            db,
            title=name,
            module="sponsor",
            action_type="create_funding_opportunity",
            description=instruction,
            payload={
                "name": name,
                "description": instruction,
                "status": "Open",
            },
            organization_id=organization_id,
            priority=priority,
        )

    return create_task(
        db,
        title=_title_from_instruction(instruction, "Review academy action"),
        module=module,
        action_type="manual_review",
        description=instruction,
        payload={"instruction": instruction, "route": route},
        organization_id=organization_id,
        priority=priority,
    )


def _management_snapshot(db: Session, organization_id: int | None) -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "organization_id": organization_id,
        "players": db.query(Player).count(),
        "parents": db.query(Parent).count(),
        "coaches": db.query(Coach).count(),
        "sponsors": db.query(Sponsor).count(),
        "funding_opportunities": db.query(FundingOpportunity).count(),
        "compliance_tasks": db.query(ComplianceTask).count(),
        "fees": db.query(Fee).count(),
        "attendance_records": db.query(Attendance).count(),
        "directors": db.query(Director).count(),
        "regulatory_filings": db.query(RegulatoryFiling).count(),
    }


def execute_task(db: Session, task: AgentTask) -> AgentTask:
    """Execute an already-approved internal action and retain the audit result."""

    if task.status != "Approved":
        raise ValueError("Task must be approved before execution")

    payload = _loads(task.payload_json)
    task.status = "Executing"
    task.error = None
    db.commit()

    try:
        if task.action_type == "create_compliance_task":
            title = str(payload.get("title") or task.title).strip()
            if not title:
                raise ValueError("Compliance task title is required")
            record = ComplianceTask(
                organization_id=task.organization_id,
                title=title,
                description=payload.get("description") or task.description,
                due_date=payload.get("due_date"),
                status=payload.get("status") or "Pending",
            )
            db.add(record)
            db.flush()
            result = {"resource": "compliance_tasks", "record_id": record.id}

        elif task.action_type == "update_npo_profile":
            record_id = int(payload.get("record_id") or 1)
            profile = db.get(NPORegulatoryProfile, record_id)
            if profile is None:
                raise ValueError(f"NPO regulatory profile {record_id} not found")
            changes = payload.get("changes") or {}
            unknown = sorted(set(changes) - NPO_EDITABLE_FIELDS)
            if unknown:
                raise ValueError(f"Unsupported NPO fields: {', '.join(unknown)}")
            if not changes:
                raise ValueError("No NPO profile changes supplied")
            for field, value in changes.items():
                setattr(profile, field, value)
            db.flush()
            result = {
                "resource": "npo_regulatory_profiles",
                "record_id": profile.id,
                "updated_fields": sorted(changes),
            }

        elif task.action_type == "create_funding_opportunity":
            name = str(payload.get("name") or payload.get("title") or task.title).strip()
            if not name:
                raise ValueError("Funding opportunity name is required")
            record = FundingOpportunity(
                organization_id=task.organization_id,
                name=name,
                title=payload.get("title") or name,
                description=payload.get("description") or task.description,
                amount=payload.get("amount"),
                deadline=payload.get("deadline"),
                sponsor_id=payload.get("sponsor_id"),
                status=payload.get("status") or "Open",
            )
            db.add(record)
            db.flush()
            result = {"resource": "funding_opportunities", "record_id": record.id}

        elif task.action_type == "prepare_parent_message":
            content = str(payload.get("content") or "").strip()
            if not content:
                raise ValueError("Message content is required")
            record = Message(
                parent_id=payload.get("parent_id"),
                content=content,
                timestamp=utc_now(),
                status="Draft",
            )
            db.add(record)
            db.flush()
            result = {
                "resource": "messages",
                "record_id": record.id,
                "status": "Draft",
                "external_delivery": False,
            }

        elif task.action_type == "generate_management_report":
            snapshot = _management_snapshot(db, task.organization_id)
            record = GeneratedReport(
                report_date=datetime.now(timezone.utc).date().isoformat(),
                report_type="Management Summary",
                content=json.dumps(snapshot, indent=2, ensure_ascii=False),
                generated_by="FAOS Agent",
                status="Draft",
            )
            db.add(record)
            db.flush()
            result = {
                "resource": "generated_reports",
                "record_id": record.id,
                "snapshot": snapshot,
            }

        elif task.action_type == "prepare_director_change":
            change_type = str(payload.get("change_type") or "").strip()
            if change_type not in {"Appointment", "Resignation", "Removal", "Replacement"}:
                raise ValueError("Unsupported director change type")
            outgoing_id = payload.get("outgoing_director_id")
            if change_type in {"Resignation", "Removal", "Replacement"} and outgoing_id is None:
                raise ValueError("Outgoing director is required")
            if outgoing_id is not None and db.get(Director, int(outgoing_id)) is None:
                raise ValueError(f"Outgoing director {outgoing_id} not found")
            incoming_first = str(payload.get("incoming_first_name") or "").strip()
            if change_type in {"Appointment", "Replacement"} and not incoming_first:
                raise ValueError("Incoming director first name is required")
            record = DirectorChangeCase(
                organization_id=task.organization_id or 1,
                change_type=change_type,
                outgoing_director_id=int(outgoing_id) if outgoing_id is not None else None,
                incoming_first_name=incoming_first or None,
                incoming_last_name=(str(payload.get("incoming_last_name") or "").strip() or None),
                incoming_role=payload.get("incoming_role") or "Director",
                meeting_date=payload.get("meeting_date"),
                resolution_date=payload.get("resolution_date"),
                resolution_reference=payload.get("resolution_reference"),
                notes=payload.get("notes") or task.description,
                status="Draft",
            )
            db.add(record)
            db.flush()
            result = {
                "resource": "director_change_cases",
                "record_id": record.id,
                "status": "Draft",
                "external_filing": False,
            }

        elif task.action_type == "record_regulatory_filing":
            regulator = str(payload.get("regulator") or "").strip()
            filing_type = str(payload.get("filing_type") or "").strip()
            if not regulator or not filing_type:
                raise ValueError("Regulator and filing_type are required")
            record = RegulatoryFiling(
                organization_id=task.organization_id or 1,
                regulator=regulator,
                filing_type=filing_type,
                reporting_period=payload.get("reporting_period"),
                due_date=payload.get("due_date"),
                filed_date=payload.get("filed_date"),
                status=payload.get("status") or "Pending",
                reference=payload.get("reference"),
                notes=payload.get("notes") or task.description,
            )
            db.add(record)
            db.flush()
            result = {"resource": "regulatory_filings", "record_id": record.id}

        elif task.action_type == "record_beneficial_ownership":
            record = BeneficialOwnershipFiling(
                organization_id=task.organization_id or 1,
                reporting_period=payload.get("reporting_period"),
                declaration_date=payload.get("declaration_date"),
                status=payload.get("status") or "Draft",
                reference=payload.get("reference"),
                security_register_status=payload.get("security_register_status"),
                notes=payload.get("notes") or task.description,
            )
            db.add(record)
            db.flush()
            result = {
                "resource": "beneficial_ownership_filings",
                "record_id": record.id,
            }

        elif task.action_type == "record_company_financial_filing":
            record = CompanyFinancialFiling(
                organization_id=task.organization_id or 1,
                reporting_period=payload.get("reporting_period"),
                filing_basis=payload.get("filing_basis") or "To Verify",
                due_date=payload.get("due_date"),
                filed_date=payload.get("filed_date"),
                status=payload.get("status") or "Draft",
                reference=payload.get("reference"),
                notes=payload.get("notes") or task.description,
            )
            db.add(record)
            db.flush()
            result = {
                "resource": "company_financial_filings",
                "record_id": record.id,
            }

        elif task.action_type == "prepare_dsd_annual_report":
            reporting_period = str(payload.get("reporting_period") or "").strip()
            if not reporting_period:
                raise ValueError("DSD reporting period is required")
            existing = (
                db.query(DSDAnnualReport)
                .filter(
                    DSDAnnualReport.organization_id == (task.organization_id or 1),
                    DSDAnnualReport.reporting_period == reporting_period,
                )
                .first()
            )
            if existing is not None:
                raise ValueError("DSD annual-report period already exists")
            record = DSDAnnualReport(
                organization_id=task.organization_id or 1,
                reporting_period=reporting_period,
                due_date=payload.get("due_date"),
                narrative_status=payload.get("narrative_status") or "Missing",
                financial_statement_status=payload.get("financial_statement_status") or "Missing",
                accounting_officer_report_status=payload.get("accounting_officer_report_status") or "Missing",
                bank_statement_status=payload.get("bank_statement_status"),
                affidavit_status=payload.get("affidavit_status"),
                submitted_date=payload.get("submitted_date"),
                status=payload.get("status") or "Draft",
                reference=payload.get("reference"),
                notes=payload.get("notes") or task.description,
            )
            db.add(record)
            db.flush()
            result = {
                "resource": "dsd_annual_reports",
                "record_id": record.id,
                "status": record.status,
            }

        elif task.action_type == "manual_review":
            result = {
                "status": "Human review recorded",
                "executed_change": False,
                "instruction": payload.get("instruction") or task.description,
            }

        else:  # pragma: no cover - create_task blocks unsupported actions
            raise ValueError(f"Unsupported action_type: {task.action_type}")

        task.status = "Completed"
        task.executed_at = utc_now()
        task.result_json = json.dumps(result, ensure_ascii=False)
        db.commit()
        db.refresh(task)
        return task

    except Exception as exc:
        db.rollback()
        failed = db.get(AgentTask, task.id)
        if failed is None:
            raise
        failed.status = "Failed"
        failed.executed_at = utc_now()
        failed.error = str(exc)
        db.commit()
        db.refresh(failed)
        return failed
