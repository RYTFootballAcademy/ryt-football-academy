"""Company governance, CIPC and DSD compliance workflows for FAOS."""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ai_agent.faos.company_models import (
    BeneficialOwnershipFiling,
    CompanyFinancialFiling,
    DirectorChangeCase,
    DSDAnnualReport,
)
from ai_agent.faos.models import Director
from ai_agent.faos.npo_models import (
    DirectorAppointmentHistory,
    GovernanceDocument,
    NPORegulatoryProfile,
    RegulatoryFiling,
)
from ai_agent.modules.database import get_db


router = APIRouter(prefix="/company", tags=["Company Governance"])

COMPLETE_STATUSES = {"Filed", "Submitted", "Complete", "Completed", "Confirmed", "Up to date"}
DIRECTOR_CHANGE_TYPES = {"Appointment", "Resignation", "Removal", "Replacement"}


class DirectorChangeCreate(BaseModel):
    organization_id: int = 1
    change_type: Literal["Appointment", "Resignation", "Removal", "Replacement"]
    outgoing_director_id: int | None = None
    incoming_first_name: str | None = None
    incoming_last_name: str | None = None
    incoming_role: str | None = "Director"
    meeting_date: str | None = None
    resolution_date: str | None = None
    resolution_reference: str | None = None
    notes: str | None = None


class DirectorChangeFiled(BaseModel):
    filed_date: str
    cipc_reference: str


class DirectorChangeConfirm(BaseModel):
    confirmed_date: str
    effective_date: str
    cipc_reference: str | None = None


class BOCreate(BaseModel):
    organization_id: int = 1
    reporting_period: str | None = None
    declaration_date: str | None = None
    status: str = "Draft"
    reference: str | None = None
    security_register_status: str | None = None
    notes: str | None = None


class FinancialFilingCreate(BaseModel):
    organization_id: int = 1
    reporting_period: str | None = None
    filing_basis: str | None = "To Verify"
    due_date: str | None = None
    filed_date: str | None = None
    status: str = "Draft"
    reference: str | None = None
    notes: str | None = None


class DSDAnnualReportCreate(BaseModel):
    organization_id: int = 1
    reporting_period: str
    due_date: str | None = None
    narrative_status: str = "Missing"
    financial_statement_status: str = "Missing"
    accounting_officer_report_status: str = "Missing"
    bank_statement_status: str | None = None
    affidavit_status: str | None = None
    submitted_date: str | None = None
    status: str = "Draft"
    reference: str | None = None
    notes: str | None = None


class FilingCreate(BaseModel):
    organization_id: int = 1
    regulator: str
    filing_type: str
    reporting_period: str | None = None
    due_date: str | None = None
    filed_date: str | None = None
    status: str = "Pending"
    reference: str | None = None
    notes: str | None = None


def _serialize(instance):
    return {column.name: getattr(instance, column.name) for column in instance.__table__.columns}


def _is_complete(status: str | None) -> bool:
    if not status:
        return False
    return status.strip().lower() in {item.lower() for item in COMPLETE_STATUSES}


@router.get("/dashboard")
def company_dashboard(
    organization_id: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
):
    profile = (
        db.query(NPORegulatoryProfile)
        .filter(NPORegulatoryProfile.organization_id == organization_id)
        .first()
    )
    directors = (
        db.query(Director)
        .filter(Director.organization_id == organization_id)
        .order_by(Director.id.asc())
        .all()
    )
    history = (
        db.query(DirectorAppointmentHistory)
        .filter(DirectorAppointmentHistory.organization_id == organization_id)
        .order_by(DirectorAppointmentHistory.id.asc())
        .all()
    )
    filings = (
        db.query(RegulatoryFiling)
        .filter(RegulatoryFiling.organization_id == organization_id)
        .order_by(RegulatoryFiling.id.desc())
        .all()
    )
    bo = (
        db.query(BeneficialOwnershipFiling)
        .filter(BeneficialOwnershipFiling.organization_id == organization_id)
        .order_by(BeneficialOwnershipFiling.id.desc())
        .all()
    )
    financials = (
        db.query(CompanyFinancialFiling)
        .filter(CompanyFinancialFiling.organization_id == organization_id)
        .order_by(CompanyFinancialFiling.id.desc())
        .all()
    )
    dsd_reports = (
        db.query(DSDAnnualReport)
        .filter(DSDAnnualReport.organization_id == organization_id)
        .order_by(DSDAnnualReport.id.desc())
        .all()
    )
    director_changes = (
        db.query(DirectorChangeCase)
        .filter(DirectorChangeCase.organization_id == organization_id)
        .order_by(DirectorChangeCase.id.desc())
        .all()
    )

    cipc_annual_returns = [
        filing
        for filing in filings
        if filing.regulator.strip().upper() == "CIPC"
        and "annual return" in filing.filing_type.strip().lower()
    ]

    blockers: list[str] = []
    if profile is None:
        blockers.append("Regulatory profile is missing.")
    else:
        if not profile.entity_type:
            blockers.append("Legal entity type has not been verified.")
        if not profile.cipc_status:
            blockers.append("Current CIPC status has not been verified.")
        if not profile.dsd_status:
            blockers.append("Current DSD NPO status has not been verified.")

    if not cipc_annual_returns:
        blockers.append("No CIPC annual-return records are registered in FAOS.")
    elif any(not _is_complete(item.status) for item in cipc_annual_returns):
        blockers.append("One or more CIPC annual-return records still require attention.")

    if not bo:
        blockers.append("No beneficial-ownership filing record is registered in the company workflow.")
    elif not _is_complete(bo[0].status):
        blockers.append("Latest beneficial-ownership record is not marked complete/filed.")

    if not financials:
        blockers.append("No AFS/FAS filing record is registered in the company workflow.")
    elif not _is_complete(financials[0].status):
        blockers.append("Latest AFS/FAS record is not marked complete/filed.")

    if not dsd_reports:
        blockers.append("No detailed DSD annual-report package is registered.")
    elif any(not _is_complete(item.status) for item in dsd_reports):
        blockers.append("One or more DSD annual-report packages still require attention.")

    if any("unverified" in (director.status or "").lower() for director in directors):
        blockers.append("The current CIPC director register is not fully verified.")

    return {
        "organization_id": organization_id,
        "generated_on": date.today().isoformat(),
        "profile": _serialize(profile) if profile else None,
        "directors": [_serialize(item) for item in directors],
        "director_history": [_serialize(item) for item in history],
        "director_changes": [_serialize(item) for item in director_changes],
        "regulatory_filings": [_serialize(item) for item in filings],
        "cipc_annual_returns": [_serialize(item) for item in cipc_annual_returns],
        "beneficial_ownership": [_serialize(item) for item in bo],
        "company_financial_filings": [_serialize(item) for item in financials],
        "dsd_annual_reports": [_serialize(item) for item in dsd_reports],
        "blockers": blockers,
        "rules": {
            "cipc_annual_returns": {
                "summary": "Track annual returns within the current CIPC anniversary filing window and retain filing confirmation.",
                "source": "CIPC Annual Returns / Beneficial Ownership guidance",
            },
            "dsd_annual_reports": {
                "summary": "Track the annual narrative, financial and accounting-officer reporting package after each financial year.",
                "source": "Department of Social Development NPO obligations",
            },
        },
    }


@router.post("/filings")
def create_regulatory_filing(payload: FilingCreate, db: Session = Depends(get_db)):
    record = RegulatoryFiling(**payload.model_dump(exclude_none=True))
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize(record)


@router.post("/beneficial-ownership")
def create_beneficial_ownership_record(payload: BOCreate, db: Session = Depends(get_db)):
    record = BeneficialOwnershipFiling(**payload.model_dump(exclude_none=True))
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize(record)


@router.post("/financial-filings")
def create_company_financial_record(payload: FinancialFilingCreate, db: Session = Depends(get_db)):
    record = CompanyFinancialFiling(**payload.model_dump(exclude_none=True))
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize(record)


@router.post("/dsd-annual-reports")
def create_dsd_annual_report(payload: DSDAnnualReportCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(DSDAnnualReport)
        .filter(
            DSDAnnualReport.organization_id == payload.organization_id,
            DSDAnnualReport.reporting_period == payload.reporting_period,
        )
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="DSD annual-report period already exists")
    record = DSDAnnualReport(**payload.model_dump(exclude_none=True))
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize(record)


@router.post("/director-changes")
def create_director_change(payload: DirectorChangeCreate, db: Session = Depends(get_db)):
    if payload.change_type not in DIRECTOR_CHANGE_TYPES:
        raise HTTPException(status_code=422, detail="Unsupported director change type")
    if payload.change_type in {"Resignation", "Removal", "Replacement"}:
        if payload.outgoing_director_id is None:
            raise HTTPException(status_code=422, detail="Outgoing director is required")
        outgoing = db.get(Director, payload.outgoing_director_id)
        if outgoing is None:
            raise HTTPException(status_code=404, detail="Outgoing director not found")
    if payload.change_type in {"Appointment", "Replacement"}:
        if not (payload.incoming_first_name or "").strip():
            raise HTTPException(status_code=422, detail="Incoming director first name is required")

    record = DirectorChangeCase(**payload.model_dump(exclude_none=True), status="Draft")
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize(record)


@router.get("/director-changes")
def list_director_changes(
    organization_id: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
):
    records = (
        db.query(DirectorChangeCase)
        .filter(DirectorChangeCase.organization_id == organization_id)
        .order_by(DirectorChangeCase.id.desc())
        .all()
    )
    return [_serialize(item) for item in records]


@router.post("/director-changes/{case_id}/ready")
def mark_director_change_ready(case_id: int, db: Session = Depends(get_db)):
    record = db.get(DirectorChangeCase, case_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Director change case not found")
    if record.status != "Draft":
        raise HTTPException(status_code=409, detail=f"Case cannot move to Ready to File from {record.status}")
    if not record.resolution_date:
        raise HTTPException(status_code=422, detail="Resolution date is required before filing readiness")
    record.status = "Ready to File"
    db.commit()
    db.refresh(record)
    return _serialize(record)


@router.post("/director-changes/{case_id}/filed")
def mark_director_change_filed(
    case_id: int,
    payload: DirectorChangeFiled,
    db: Session = Depends(get_db),
):
    record = db.get(DirectorChangeCase, case_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Director change case not found")
    if record.status != "Ready to File":
        raise HTTPException(status_code=409, detail=f"Case cannot be filed from {record.status}")
    record.status = "Filed - Awaiting CIPC Confirmation"
    record.filed_date = payload.filed_date
    record.cipc_reference = payload.cipc_reference
    db.commit()
    db.refresh(record)
    return _serialize(record)


@router.post("/director-changes/{case_id}/confirm")
def confirm_director_change(
    case_id: int,
    payload: DirectorChangeConfirm,
    db: Session = Depends(get_db),
):
    record = db.get(DirectorChangeCase, case_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Director change case not found")
    if record.status != "Filed - Awaiting CIPC Confirmation":
        raise HTTPException(status_code=409, detail=f"Case cannot be confirmed from {record.status}")

    reference = payload.cipc_reference or record.cipc_reference
    if not reference:
        raise HTTPException(status_code=422, detail="CIPC confirmation reference is required")

    if record.outgoing_director_id is not None:
        outgoing = db.get(Director, record.outgoing_director_id)
        if outgoing is not None:
            outgoing.status = "Historical - CIPC change confirmed"
            history = (
                db.query(DirectorAppointmentHistory)
                .filter(
                    DirectorAppointmentHistory.organization_id == record.organization_id,
                    DirectorAppointmentHistory.director_id == outgoing.id,
                    DirectorAppointmentHistory.resignation_date.is_(None),
                )
                .order_by(DirectorAppointmentHistory.id.desc())
                .first()
            )
            if history is not None:
                history.resignation_date = payload.effective_date
                history.status = "Historical - CIPC change confirmed"
                history.notes = (
                    ((history.notes or "") + " ").strip()
                    + f"Director change confirmed under CIPC reference {reference}."
                ).strip()

    if record.change_type in {"Appointment", "Replacement"}:
        incoming = Director(
            organization_id=record.organization_id,
            first_name=(record.incoming_first_name or "").strip(),
            last_name=(record.incoming_last_name or "").strip() or None,
            role=record.incoming_role or "Director",
            status="Active - CIPC verified",
        )
        db.add(incoming)
        db.flush()
        record.incoming_director_id = incoming.id
        db.add(
            DirectorAppointmentHistory(
                organization_id=record.organization_id,
                director_id=incoming.id,
                appointment_date=payload.effective_date,
                appointment_source="CIPC director amendment",
                appointment_reference=reference,
                status="Active - CIPC verified",
                notes="Created only after explicit CIPC confirmation was recorded in FAOS.",
            )
        )

    record.status = "Confirmed"
    record.confirmed_date = payload.confirmed_date
    record.effective_date = payload.effective_date
    record.cipc_reference = reference
    db.commit()
    db.refresh(record)
    return _serialize(record)
