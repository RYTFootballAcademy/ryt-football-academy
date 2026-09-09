"""Typed, persistent CRM API for the RYT Football Academy FAOS."""

from __future__ import annotations

from typing import TypeVar

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ai_agent.modules.database import get_db
from .models import (
    Attendance,
    Camp,
    Coach,
    ComplianceTask,
    Fee,
    FundingOpportunity,
    Message,
    Parent,
    Player,
    Product,
    Proposal,
    Sponsor,
    Tournament,
    Trial,
)
from .schemas import (
    AttendanceCreate,
    AttendanceRead,
    CampCreate,
    CampRead,
    CoachCreate,
    CoachRead,
    ComplianceCreate,
    ComplianceRead,
    FeeCreate,
    FeeRead,
    FundingCreate,
    FundingRead,
    MessageCreate,
    MessageRead,
    ParentCreate,
    ParentRead,
    PlayerCreate,
    PlayerRead,
    ProductCreate,
    ProductRead,
    ProposalCreate,
    ProposalRead,
    SponsorCreate,
    SponsorRead,
    SponsorStatusUpdate,
    TournamentCreate,
    TournamentRead,
    TrialCreate,
    TrialRead,
)

router = APIRouter(prefix="/crm", tags=["CRM"])
T = TypeVar("T")


def _save(db: Session, instance: T) -> T:
    try:
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc.orig)) from exc


def _list(db: Session, model, limit: int = 100):
    return db.query(model).order_by(model.id.desc()).limit(min(limit, 500)).all()


@router.get("/summary")
def crm_summary(db: Session = Depends(get_db)):
    models = {
        "players": Player,
        "parents": Parent,
        "coaches": Coach,
        "sponsors": Sponsor,
        "funding_opportunities": FundingOpportunity,
        "compliance_tasks": ComplianceTask,
        "proposals": Proposal,
        "tournaments": Tournament,
        "fees": Fee,
        "trials": Trial,
        "attendance": Attendance,
        "messages": Message,
        "products": Product,
        "camps": Camp,
    }
    return {name: db.query(model).count() for name, model in models.items()}


@router.post("/parent", response_model=ParentRead, status_code=status.HTTP_201_CREATED)
@router.post("/parents", response_model=ParentRead, status_code=status.HTTP_201_CREATED)
def create_parent(payload: ParentCreate, db: Session = Depends(get_db)):
    return _save(db, Parent(**payload.model_dump(exclude_none=True)))


@router.get("/parents", response_model=list[ParentRead])
def list_parents(limit: int = 100, db: Session = Depends(get_db)):
    return _list(db, Parent, limit)


@router.post("/player", response_model=PlayerRead, status_code=status.HTTP_201_CREATED)
@router.post("/players", response_model=PlayerRead, status_code=status.HTTP_201_CREATED)
def create_player(payload: PlayerCreate, db: Session = Depends(get_db)):
    return _save(db, Player(**payload.model_dump(exclude_none=True)))


@router.get("/players", response_model=list[PlayerRead])
def list_players(limit: int = 100, db: Session = Depends(get_db)):
    return _list(db, Player, limit)


@router.post("/coach", response_model=CoachRead, status_code=status.HTTP_201_CREATED)
@router.post("/coaches", response_model=CoachRead, status_code=status.HTTP_201_CREATED)
def create_coach(payload: CoachCreate, db: Session = Depends(get_db)):
    return _save(db, Coach(**payload.model_dump(exclude_none=True)))


@router.get("/coaches", response_model=list[CoachRead])
def list_coaches(limit: int = 100, db: Session = Depends(get_db)):
    return _list(db, Coach, limit)


@router.post("/sponsor", response_model=SponsorRead, status_code=status.HTTP_201_CREATED)
@router.post("/sponsors", response_model=SponsorRead, status_code=status.HTTP_201_CREATED)
def create_sponsor(payload: SponsorCreate, db: Session = Depends(get_db)):
    return _save(db, Sponsor(**payload.model_dump(exclude_none=True)))


@router.get("/sponsors", response_model=list[SponsorRead])
def list_sponsors(limit: int = 100, db: Session = Depends(get_db)):
    return _list(db, Sponsor, limit)


@router.get("/sponsors/{sponsor_id}", response_model=SponsorRead)
def get_sponsor(sponsor_id: int, db: Session = Depends(get_db)):
    sponsor = db.get(Sponsor, sponsor_id)
    if sponsor is None:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    return sponsor


@router.patch("/sponsors/{sponsor_id}/status", response_model=SponsorRead)
def update_sponsor_status(
    sponsor_id: int,
    payload: SponsorStatusUpdate,
    db: Session = Depends(get_db),
):
    sponsor = db.get(Sponsor, sponsor_id)
    if sponsor is None:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    sponsor.status = payload.status
    return _save(db, sponsor)


@router.delete("/sponsors/{sponsor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sponsor(sponsor_id: int, db: Session = Depends(get_db)):
    sponsor = db.get(Sponsor, sponsor_id)
    if sponsor is None:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    db.delete(sponsor)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/funding", response_model=FundingRead, status_code=status.HTTP_201_CREATED)
@router.post("/funding-opportunities", response_model=FundingRead, status_code=status.HTTP_201_CREATED)
def create_funding(payload: FundingCreate, db: Session = Depends(get_db)):
    return _save(db, FundingOpportunity(**payload.model_dump(exclude_none=True)))


@router.get("/funding", response_model=list[FundingRead])
def list_funding(limit: int = 100, db: Session = Depends(get_db)):
    return _list(db, FundingOpportunity, limit)


@router.post("/compliance", response_model=ComplianceRead, status_code=status.HTTP_201_CREATED)
def create_compliance(payload: ComplianceCreate, db: Session = Depends(get_db)):
    return _save(db, ComplianceTask(**payload.model_dump(exclude_none=True)))


@router.get("/compliance", response_model=list[ComplianceRead])
def list_compliance(limit: int = 100, db: Session = Depends(get_db)):
    return _list(db, ComplianceTask, limit)


@router.post("/proposal", response_model=ProposalRead, status_code=status.HTTP_201_CREATED)
@router.post("/proposals", response_model=ProposalRead, status_code=status.HTTP_201_CREATED)
def create_proposal(payload: ProposalCreate, db: Session = Depends(get_db)):
    return _save(db, Proposal(**payload.model_dump(exclude_none=True)))


@router.get("/proposals", response_model=list[ProposalRead])
def list_proposals(limit: int = 100, db: Session = Depends(get_db)):
    return _list(db, Proposal, limit)


@router.post("/tournament", response_model=TournamentRead, status_code=status.HTTP_201_CREATED)
@router.post("/tournaments", response_model=TournamentRead, status_code=status.HTTP_201_CREATED)
def create_tournament(payload: TournamentCreate, db: Session = Depends(get_db)):
    return _save(db, Tournament(**payload.model_dump(exclude_none=True)))


@router.get("/tournaments", response_model=list[TournamentRead])
def list_tournaments(limit: int = 100, db: Session = Depends(get_db)):
    return _list(db, Tournament, limit)


@router.post("/fee", response_model=FeeRead, status_code=status.HTTP_201_CREATED)
@router.post("/fees", response_model=FeeRead, status_code=status.HTTP_201_CREATED)
def create_fee(payload: FeeCreate, db: Session = Depends(get_db)):
    return _save(db, Fee(**payload.model_dump(exclude_none=True)))


@router.get("/fees", response_model=list[FeeRead])
def list_fees(limit: int = 100, db: Session = Depends(get_db)):
    return _list(db, Fee, limit)


@router.post("/trial", response_model=TrialRead, status_code=status.HTTP_201_CREATED)
@router.post("/trials", response_model=TrialRead, status_code=status.HTTP_201_CREATED)
def create_trial(payload: TrialCreate, db: Session = Depends(get_db)):
    return _save(db, Trial(**payload.model_dump(exclude_none=True)))


@router.get("/trials", response_model=list[TrialRead])
def list_trials(limit: int = 100, db: Session = Depends(get_db)):
    return _list(db, Trial, limit)


@router.post("/attendance", response_model=AttendanceRead, status_code=status.HTTP_201_CREATED)
def create_attendance(payload: AttendanceCreate, db: Session = Depends(get_db)):
    return _save(db, Attendance(**payload.model_dump(exclude_none=True)))


@router.get("/attendance", response_model=list[AttendanceRead])
def list_attendance(limit: int = 100, db: Session = Depends(get_db)):
    return _list(db, Attendance, limit)


@router.post("/message", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
@router.post("/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def create_message(payload: MessageCreate, db: Session = Depends(get_db)):
    return _save(db, Message(**payload.model_dump(exclude_none=True)))


@router.get("/messages", response_model=list[MessageRead])
def list_messages(limit: int = 100, db: Session = Depends(get_db)):
    return _list(db, Message, limit)


@router.post("/product", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    return _save(db, Product(**payload.model_dump(exclude_none=True)))


@router.get("/products", response_model=list[ProductRead])
def list_products(limit: int = 100, db: Session = Depends(get_db)):
    return _list(db, Product, limit)


@router.post("/camp", response_model=CampRead, status_code=status.HTTP_201_CREATED)
@router.post("/camps", response_model=CampRead, status_code=status.HTTP_201_CREATED)
def create_camp(payload: CampCreate, db: Session = Depends(get_db)):
    return _save(db, Camp(**payload.model_dump(exclude_none=True)))


@router.get("/camps", response_model=list[CampRead])
def list_camps(limit: int = 100, db: Session = Depends(get_db)):
    return _list(db, Camp, limit)
