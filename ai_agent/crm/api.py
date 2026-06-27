from fastapi import APIRouter
from .crm_service import (
    register_player, register_parent,
    record_fee, record_trial, create_tournament
)

router = APIRouter(prefix="/crm", tags=["CRM"])

@router.post("/player")
def create_player(name: str, age: int, position: str, parent_id: int = None):
    return register_player(name, age, position, parent_id)

@router.post("/parent")
def create_parent(name: str, contact: str):
    return register_parent(name, contact)

@router.post("/fee")
def add_fee(player_id: int, amount: float, status: str, due_date: str):
    return record_fee(player_id, amount, status, due_date)

@router.post("/trial")
def add_trial(player_id: int, date: str, result: str = None):
    return record_trial(player_id, date, result)

@router.post("/tournament")
def add_tournament(name: str, start_date: str, end_date: str):
    return create_tournament(name, start_date, end_date)
