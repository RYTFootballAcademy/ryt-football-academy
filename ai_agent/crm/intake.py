"""Player and guardian intake workflows for FAOS."""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ai_agent.faos.models import Team
from ai_agent.modules.database import get_db
from .models import Parent, Player, PlayerIntakeStatus


router = APIRouter(prefix="/crm/intake", tags=["Player Intake"])

FormStatus = Literal["Missing", "Pending", "Received", "Signed", "Not Applicable"]
COMPLETE_FORM_STATUSES = {"Received", "Signed", "Not Applicable"}


class GuardianIntake(BaseModel):
    parent_id: int | None = None
    name: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    email: str | None = None
    relationship_to_player: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    emergency_contact_relationship: str | None = None


class PlayerIntakeData(BaseModel):
    name: str
    first_name: str | None = None
    last_name: str | None = None
    age: int | None = Field(default=None, ge=0, le=100)
    dob: str | None = None
    gender: str | None = None
    team_id: int | None = None
    position: str | None = None
    school: str | None = None
    grade: str | None = None
    allergies: str | None = None
    injuries: str | None = None
    medication: str | None = None
    registration_date: str | None = None
    status: str = "Active"
    notes: str | None = None


class FormStatusData(BaseModel):
    registration_form_status: FormStatus = "Missing"
    medical_form_status: FormStatus = "Missing"
    emergency_contact_form_status: FormStatus = "Missing"
    media_consent_status: FormStatus = "Missing"
    indemnity_form_status: FormStatus = "Missing"
    medical_info_confirmed: bool = False
    notes: str | None = None


class PlayerIntakeRequest(BaseModel):
    organization_id: int = 1
    player: PlayerIntakeData
    guardian: GuardianIntake | None = None
    forms: FormStatusData = Field(default_factory=FormStatusData)
    allow_duplicate: bool = False


class BulkIntakeRequest(BaseModel):
    records: list[PlayerIntakeRequest] = Field(min_length=1, max_length=100)


class FormStatusUpdate(BaseModel):
    registration_form_status: FormStatus | None = None
    medical_form_status: FormStatus | None = None
    emergency_contact_form_status: FormStatus | None = None
    media_consent_status: FormStatus | None = None
    indemnity_form_status: FormStatus | None = None
    medical_info_confirmed: bool | None = None
    notes: str | None = None


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _resolve_guardian(db: Session, data: GuardianIntake | None, organization_id: int) -> Parent | None:
    if data is None:
        return None

    if data.parent_id is not None:
        parent = db.get(Parent, data.parent_id)
        if parent is None:
            raise ValueError(f"Parent {data.parent_id} not found")
        return parent

    name = _clean(data.name)
    if not name:
        raise ValueError("Guardian name is required when parent_id is not supplied")

    phone = _clean(data.phone)
    email = _clean(data.email)
    parent = None

    if phone:
        parent = (
            db.query(Parent)
            .filter(func.lower(Parent.name) == name.lower(), Parent.phone == phone)
            .first()
        )
    if parent is None and email:
        parent = (
            db.query(Parent)
            .filter(func.lower(Parent.name) == name.lower(), func.lower(Parent.email) == email.lower())
            .first()
        )

    values = {
        "organization_id": organization_id,
        "name": name,
        "phone": phone,
        "whatsapp": _clean(data.whatsapp),
        "email": email,
        "relationship_to_player": _clean(data.relationship_to_player),
        "emergency_contact_name": _clean(data.emergency_contact_name),
        "emergency_contact_phone": _clean(data.emergency_contact_phone),
        "emergency_contact_relationship": _clean(data.emergency_contact_relationship),
    }

    if parent is None:
        parent = Parent(**values)
        db.add(parent)
        db.flush()
    else:
        # Reuse known guardians and only fill fields that are currently blank.
        for key, value in values.items():
            if value is not None and getattr(parent, key, None) in (None, ""):
                setattr(parent, key, value)

    return parent


def _validate_team(db: Session, team_id: int | None) -> None:
    if team_id is not None and db.get(Team, team_id) is None:
        raise ValueError(f"Team {team_id} not found")


def _find_duplicate(
    db: Session,
    player: PlayerIntakeData,
    parent_id: int | None,
) -> Player | None:
    name = player.name.strip()
    query = db.query(Player).filter(func.lower(Player.name) == name.lower())

    if player.dob:
        return query.filter(Player.dob == player.dob).first()
    if parent_id is not None:
        return query.filter(Player.parent_id == parent_id).first()
    return None


def _create_intake(db: Session, payload: PlayerIntakeRequest) -> dict:
    _validate_team(db, payload.player.team_id)
    guardian = _resolve_guardian(db, payload.guardian, payload.organization_id)

    if not payload.allow_duplicate:
        duplicate = _find_duplicate(
            db,
            payload.player,
            guardian.id if guardian is not None else None,
        )
        if duplicate is not None:
            raise ValueError(
                f"Possible duplicate player found: {duplicate.name} (id {duplicate.id})"
            )

    player_values = payload.player.model_dump(exclude_none=True)
    player_values["name"] = payload.player.name.strip()
    player_values["organization_id"] = payload.organization_id
    if guardian is not None:
        player_values["parent_id"] = guardian.id
    if "registration_date" not in player_values:
        player_values["registration_date"] = date.today().isoformat()

    player = Player(**player_values)
    db.add(player)
    db.flush()

    form_values = payload.forms.model_dump()
    form_values["player_id"] = player.id
    form_values["last_reviewed_date"] = date.today().isoformat()
    intake_status = PlayerIntakeStatus(**form_values)
    db.add(intake_status)
    db.flush()

    return {
        "player_id": player.id,
        "player_name": player.name,
        "parent_id": guardian.id if guardian is not None else None,
        "intake_status_id": intake_status.id,
        "team_id": player.team_id,
    }


def _readiness_for_player(db: Session, player: Player) -> dict:
    parent = db.get(Parent, player.parent_id) if player.parent_id else None
    forms = (
        db.query(PlayerIntakeStatus)
        .filter(PlayerIntakeStatus.player_id == player.id)
        .first()
    )

    checks: list[tuple[str, bool]] = [
        ("guardian", parent is not None),
        (
            "guardian_phone",
            parent is not None and bool(parent.phone or parent.whatsapp),
        ),
        (
            "emergency_contact",
            parent is not None and bool(parent.emergency_contact_phone),
        ),
        ("team_assignment", player.team_id is not None),
        ("dob_or_age", bool(player.dob) or player.age is not None),
        ("school", bool(player.school)),
        ("grade", bool(player.grade)),
        (
            "medical_information_confirmed",
            forms is not None and bool(forms.medical_info_confirmed),
        ),
        (
            "registration_form",
            forms is not None
            and forms.registration_form_status in COMPLETE_FORM_STATUSES,
        ),
        (
            "medical_form",
            forms is not None and forms.medical_form_status in COMPLETE_FORM_STATUSES,
        ),
        (
            "emergency_contact_form",
            forms is not None
            and forms.emergency_contact_form_status in COMPLETE_FORM_STATUSES,
        ),
        (
            "media_consent",
            forms is not None and forms.media_consent_status in COMPLETE_FORM_STATUSES,
        ),
        (
            "indemnity_form",
            forms is not None and forms.indemnity_form_status in COMPLETE_FORM_STATUSES,
        ),
    ]
    missing = [name for name, passed in checks if not passed]
    completed = len(checks) - len(missing)
    percentage = round((completed / len(checks)) * 100)

    return {
        "player_id": player.id,
        "player_name": player.name,
        "team_id": player.team_id,
        "parent_id": player.parent_id,
        "completeness_percent": percentage,
        "complete": not missing,
        "missing": missing,
    }


@router.post("/player", status_code=status.HTTP_201_CREATED)
def create_player_intake(payload: PlayerIntakeRequest, db: Session = Depends(get_db)):
    try:
        result = _create_intake(db, payload)
        db.commit()
        return result
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        db.rollback()
        raise


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def bulk_player_intake(payload: BulkIntakeRequest, db: Session = Depends(get_db)):
    created: list[dict] = []
    errors: list[dict] = []

    for index, record in enumerate(payload.records):
        try:
            result = _create_intake(db, record)
            db.commit()
            created.append({"index": index, **result})
        except Exception as exc:
            db.rollback()
            errors.append(
                {
                    "index": index,
                    "player_name": record.player.name,
                    "error": str(exc),
                }
            )

    return {
        "requested": len(payload.records),
        "created_count": len(created),
        "error_count": len(errors),
        "created": created,
        "errors": errors,
    }


@router.get("/readiness")
def player_intake_readiness(
    organization_id: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
):
    players = (
        db.query(Player)
        .filter(
            or_(
                Player.organization_id == organization_id,
                Player.organization_id.is_(None),
            )
        )
        .order_by(Player.name.asc())
        .all()
    )
    records = [_readiness_for_player(db, player) for player in players]
    return {
        "organization_id": organization_id,
        "players": len(records),
        "complete": sum(item["complete"] for item in records),
        "incomplete": sum(not item["complete"] for item in records),
        "records": records,
    }


@router.patch("/{player_id}/forms")
def update_form_status(
    player_id: int,
    payload: FormStatusUpdate,
    db: Session = Depends(get_db),
):
    player = db.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    record = (
        db.query(PlayerIntakeStatus)
        .filter(PlayerIntakeStatus.player_id == player_id)
        .first()
    )
    if record is None:
        record = PlayerIntakeStatus(player_id=player_id)
        db.add(record)

    values = payload.model_dump(exclude_none=True)
    for key, value in values.items():
        setattr(record, key, value)
    record.last_reviewed_date = date.today().isoformat()

    db.commit()
    db.refresh(record)
    return _readiness_for_player(db, player)
