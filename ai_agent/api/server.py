from typing import List
from fastapi import FastAPI, Depends
from ai_agent.crm.api import router as crm_router
from fastapi import APIRouter
from ai_agent.modules.sponsor_manager import SponsorManager, Sponsor

from sqlalchemy.orm import Session
from ai_agent.modules.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="RYT Football Academy AI System", version="1.0")

# Include CRM routes
app.include_router(crm_router)

# Example sponsor routes
router = APIRouter()
sponsor_manager = SponsorManager()

@router.post("/sponsor/add")
def add_sponsor(sponsor: Sponsor):
    return sponsor_manager.add_sponsor(sponsor)

@router.get("/sponsor/list")
def list_sponsors():
    return sponsor_manager.list_sponsors()

@router.put("/sponsor/{sponsor_id}/status")
def update_status(sponsor_id: int, new_status: str):
    return sponsor_manager.update_status(sponsor_id, new_status)

app.include_router(router, prefix="/sponsor")
from ai_agent.modules.proposal_generator import ProposalGenerator

proposal_generator = ProposalGenerator()

@app.post("/proposal/generate")
def generate_proposal(sponsor_name: str, contribution_amount: float):
    return proposal_generator.generate_proposal(sponsor_name, contribution_amount)
from ai_agent.modules.funding_finder import FundingFinder

funding_finder = FundingFinder()

@app.post("/funding/add")
def add_opportunity(category: str, name: str, description: str, contact: str):
    return funding_finder.add_opportunity(category, name, description, contact)

@app.get("/funding/list")
def list_opportunities():
    return funding_finder.list_opportunities()

@app.get("/funding/category/{category}")
def find_by_category(category: str):
    return funding_finder.find_by_category(category)
from ai_agent.modules.npo_compliance import NPOComplianceTracker

npo_tracker = NPOComplianceTracker()

@app.post("/npo/director/add")
def add_director(name: str):
    return npo_tracker.add_director(name)

@app.post("/npo/member/add")
def add_member(name: str):
    return npo_tracker.add_member(name)

@app.post("/npo/meeting/record")
def record_meeting(date: str, attendees: List[str]):
    return npo_tracker.record_meeting(date, attendees)

@app.put("/npo/director/inactive")
def mark_inactive_director(name: str):
    return npo_tracker.mark_inactive_director(name)

@app.post("/npo/task/add")
def add_task(task: str, due_date: str):
    return npo_tracker.add_task(task, due_date)

@app.put("/npo/task/complete")
def complete_task(task: str):
    return npo_tracker.complete_task(task)

@app.get("/npo/tasks")
def list_tasks():
    return npo_tracker.list_tasks()

from ai_agent.crm.models import Coach

@app.post("/crm/coach")
def create_coach(name: str, role: str, phone: str, email: str, db: Session = Depends(get_db)):
    coach = Coach(name=name, role=role, phone=phone, email=email)
    db.add(coach)
    db.commit()
    db.refresh(coach)
    return coach

from ai_agent.crm.models import Sponsor

@app.post("/crm/sponsor")
def create_sponsor(
    name: str,
    industry: str,
    contact_person: str,
    email: str,
    phone: str,
    db: Session = Depends(get_db)
):
    sponsor = Sponsor(
        name=name,
        industry=industry,
        contact_person=contact_person,
        email=email,
        phone=phone
    )
    db.add(sponsor)
    db.commit()
    db.refresh(sponsor)
    return sponsor

from ai_agent.crm.models import FundingOpportunity

@app.post("/crm/funding")
def create_funding(
    title: str,
    description: str,
    amount: int,
    sponsor_id: int,
    db: Session = Depends(get_db)
):
    funding = FundingOpportunity(
        title=title,
        description=description,
        amount=amount,
        sponsor_id=sponsor_id
    )
    db.add(funding)
    db.commit()
    db.refresh(funding)
    return funding

from ai_agent.crm.models import ComplianceTask

@app.post("/crm/compliance")
def create_compliance(
    title: str,
    description: str,
    due_date: str,
    status: str,
    db: Session = Depends(get_db)
):
    task = ComplianceTask(
        title=title,
        description=description,
        due_date=due_date,
        status=status
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

from ai_agent.crm.models import Proposal

@app.post("/crm/proposal")
def create_proposal(
    title: str,
    content: str,
    sponsor_id: int,
    funding_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    proposal = Proposal(
        title=title,
        content=content,
        sponsor_id=sponsor_id,
        funding_id=funding_id,
        status=status
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal

from ai_agent.crm.models import Tournament

@app.post("/crm/tournament")
def create_tournament(
    name: str,
    location: str,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    tournament = Tournament(
        name=name,
        location=location,
        start_date=start_date,
        end_date=end_date
    )
    db.add(tournament)
    db.commit()
    db.refresh(tournament)
    return tournament

from ai_agent.crm.models import Fee

@app.post("/crm/fee")
def create_fee(
    player_id: int,
    amount: int,
    due_date: str,
    status: str,
    db: Session = Depends(get_db)
):
    fee = Fee(player_id=player_id, amount=amount, due_date=due_date, status=status)
    db.add(fee)
    db.commit()
    db.refresh(fee)
    return fee

from ai_agent.crm.models import Trial

@app.post("/crm/trial")
def create_trial(
    player_id: int,
    date: str,
    result: str,
    notes: str,
    db: Session = Depends(get_db)
):
    trial = Trial(player_id=player_id, date=date, result=result, notes=notes)
    db.add(trial)
    db.commit()
    db.refresh(trial)
    return trial

from ai_agent.crm.models import Attendance

@app.post("/crm/attendance")
def create_attendance(
    player_id: int,
    date: str,
    status: str,
    db: Session = Depends(get_db)
):
    attendance = Attendance(player_id=player_id, date=date, status=status)
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance

from ai_agent.crm.models import Message

@app.post("/crm/message")
def create_message(
    sender_id: int,
    receiver_id: int,
    content: str,
    timestamp: str,
    db: Session = Depends(get_db)
):
    message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
        timestamp=timestamp
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

from ai_agent.crm.models import Product

@app.post("/crm/product")
def create_product(
    name: str,
    price: int,
    stock: int,
    db: Session = Depends(get_db)
):
    product = Product(name=name, price=price, stock=stock)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
