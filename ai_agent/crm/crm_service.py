"""Service-layer helpers for core academy CRM operations."""

from __future__ import annotations

from typing import Optional

from ai_agent.modules.database import session_scope
from .models import Fee, Parent, Player, Sponsor, Tournament, Trial


def register_player(
    name: str,
    age: Optional[int] = None,
    position: Optional[str] = None,
    parent_id: Optional[int] = None,
):
    with session_scope() as db:
        player = Player(name=name, age=age, position=position, parent_id=parent_id)
        db.add(player)
        db.flush()
        db.refresh(player)
        db.expunge(player)
        return player


def register_parent(name: str, phone: Optional[str] = None, email: Optional[str] = None):
    with session_scope() as db:
        parent = Parent(name=name, phone=phone, email=email)
        db.add(parent)
        db.flush()
        db.refresh(parent)
        db.expunge(parent)
        return parent


def record_fee(player_id: int, amount: int, status: str, due_date: Optional[str] = None):
    with session_scope() as db:
        fee = Fee(player_id=player_id, amount=amount, status=status, due_date=due_date)
        db.add(fee)
        db.flush()
        db.refresh(fee)
        db.expunge(fee)
        return fee


def record_trial(
    player_id: int,
    date: Optional[str],
    result: Optional[str] = None,
    notes: Optional[str] = None,
):
    with session_scope() as db:
        trial = Trial(player_id=player_id, date=date, result=result, notes=notes)
        db.add(trial)
        db.flush()
        db.refresh(trial)
        db.expunge(trial)
        return trial


def create_tournament(
    name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    location: Optional[str] = None,
):
    with session_scope() as db:
        tournament = Tournament(
            name=name,
            start_date=start_date,
            end_date=end_date,
            location=location,
        )
        db.add(tournament)
        db.flush()
        db.refresh(tournament)
        db.expunge(tournament)
        return tournament


def create_sponsor(
    name: str,
    industry: Optional[str] = None,
    contact_person: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    website: Optional[str] = None,
    status: str = "Prospect",
):
    with session_scope() as db:
        sponsor = Sponsor(
            name=name,
            industry=industry,
            contact_person=contact_person,
            email=email,
            phone=phone,
            website=website,
            status=status,
        )
        db.add(sponsor)
        db.flush()
        db.refresh(sponsor)
        db.expunge(sponsor)
        return sponsor
