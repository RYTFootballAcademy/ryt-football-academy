"""Prepare and audit local external-portal workflows.

FAOS never stores passwords, OTPs, payment-card data, cookies or security
answers. The visible browser assistant is launched separately from the local
command line after a workflow is prepared.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ai_agent.faos.company_models import (
    ExternalPortalWorkflow,
    ExternalPortalWorkflowEvent,
)
from ai_agent.faos.npo_models import NPORegulatoryProfile
from ai_agent.modules.database import get_db


router = APIRouter(prefix="/portal", tags=["External Portal Agent"])

WORKFLOW_TYPES = {
    "cipc_reinstatement",
    "cipc_annual_return",
    "cipc_beneficial_ownership",
    "cipc_director_change",
    "information_regulator",
}

WORKFLOW_TITLES = {
    "cipc_reinstatement": "CIPC reinstatement",
    "cipc_annual_return": "CIPC annual return",
    "cipc_beneficial_ownership": "CIPC beneficial ownership",
    "cipc_director_change": "CIPC director change",
    "information_regulator": "Information Regulator registration",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class PortalWorkflowCreate(BaseModel):
    organization_id: int = 1
    workflow_type: Literal[
        "cipc_reinstatement",
        "cipc_annual_return",
        "cipc_beneficial_ownership",
        "cipc_director_change",
        "information_regulator",
    ]
    registration_number: str | None = None
    notes: str | None = None


class PortalReferenceUpdate(BaseModel):
    external_reference: str
    status: str | None = None


def _serialize(record):
    return {column.name: getattr(record, column.name) for column in record.__table__.columns}


def _add_event(db: Session, workflow_id: int, event_type: str, message: str) -> None:
    db.add(
        ExternalPortalWorkflowEvent(
            workflow_id=workflow_id,
            event_time=utc_now(),
            event_type=event_type,
            message=message,
        )
    )
    db.commit()


@router.post("/workflows", status_code=status.HTTP_201_CREATED)
def prepare_portal_workflow(payload: PortalWorkflowCreate, db: Session = Depends(get_db)):
    if payload.workflow_type not in WORKFLOW_TYPES:
        raise HTTPException(status_code=422, detail="Unsupported portal workflow")

    registration_number = (payload.registration_number or "").strip() or None
    if registration_number is None and payload.workflow_type.startswith("cipc_"):
        profile = (
            db.query(NPORegulatoryProfile)
            .filter(NPORegulatoryProfile.organization_id == payload.organization_id)
            .first()
        )
        if profile is not None:
            registration_number = profile.cipc_registration_number

    if payload.workflow_type.startswith("cipc_") and not registration_number:
        raise HTTPException(
            status_code=422,
            detail="CIPC registration number is required for this workflow",
        )

    service = (
        "Information Regulator"
        if payload.workflow_type == "information_regulator"
        else "BizPortal / CIPC"
    )

    now = utc_now()
    record = ExternalPortalWorkflow(
        organization_id=payload.organization_id,
        service=service,
        workflow_type=payload.workflow_type,
        registration_number=registration_number,
        status="Prepared",
        current_step="Ready to launch controlled browser",
        requires_user_login=True,
        requires_user_approval=True,
        created_at=now,
        updated_at=now,
        notes=payload.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    _add_event(
        db,
        record.id,
        "prepared",
        (
            f"{WORKFLOW_TITLES[payload.workflow_type]} workflow prepared. "
            "No external portal action has been taken."
        ),
    )

    response = _serialize(record)
    response["launch_command"] = (
        f"python scripts\\bizportal_agent.py --workflow-id {record.id}"
    )
    response["security"] = (
        "Enter CIPC password, OTP/security answers and payment-card details only "
        "in the visible browser. FAOS does not store them."
    )
    return response


@router.get("/workflows")
def list_portal_workflows(
    organization_id: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    records = (
        db.query(ExternalPortalWorkflow)
        .filter(ExternalPortalWorkflow.organization_id == organization_id)
        .order_by(ExternalPortalWorkflow.id.desc())
        .limit(limit)
        .all()
    )
    return [_serialize(record) for record in records]


@router.get("/workflows/{workflow_id}")
def get_portal_workflow(workflow_id: int, db: Session = Depends(get_db)):
    record = db.get(ExternalPortalWorkflow, workflow_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Portal workflow not found")
    result = _serialize(record)
    result["launch_command"] = (
        f"python scripts\\bizportal_agent.py --workflow-id {record.id}"
    )
    return result


@router.get("/workflows/{workflow_id}/events")
def get_portal_workflow_events(workflow_id: int, db: Session = Depends(get_db)):
    if db.get(ExternalPortalWorkflow, workflow_id) is None:
        raise HTTPException(status_code=404, detail="Portal workflow not found")
    records = (
        db.query(ExternalPortalWorkflowEvent)
        .filter(ExternalPortalWorkflowEvent.workflow_id == workflow_id)
        .order_by(ExternalPortalWorkflowEvent.id.asc())
        .all()
    )
    return [_serialize(record) for record in records]


@router.patch("/workflows/{workflow_id}/reference")
def update_portal_reference(
    workflow_id: int,
    payload: PortalReferenceUpdate,
    db: Session = Depends(get_db),
):
    record = db.get(ExternalPortalWorkflow, workflow_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Portal workflow not found")
    record.external_reference = payload.external_reference.strip()
    if payload.status:
        record.status = payload.status
    record.updated_at = utc_now()
    db.commit()
    db.refresh(record)
    _add_event(
        db,
        record.id,
        "reference_updated",
        "External regulator reference was recorded by the user.",
    )
    return _serialize(record)
