"""
RYT Football Academy - FastAPI Backend
--------------------------------------
This is the central API layer connecting all AI modules:
- Core Agent
- NPO Manager
- Sponsor Engine
- WhatsApp Hub

This turns the system into a runnable backend service.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List

# Import modules (local package structure)
from ai_agent.core.agent import RYTAI_Agent, Task
from ai_agent.modules.npo_manager import NPOManager
from ai_agent.modules.sponsor_engine import SponsorEngine
from ai_agent.modules.whatsapp_hub import WhatsAppHub


app = FastAPI(title="RYT Football Academy AI System", version="1.0")

# Initialize systems
agent = RYTAI_Agent()
npo = NPOManager()
sponsors = SponsorEngine()
whatsapp = WhatsAppHub()


# ---------------- REQUEST MODELS ----------------

class ChatRequest(BaseModel):
    message: str


class SponsorLeadRequest(BaseModel):
    name: str
    industry: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class WhatsAppRequest(BaseModel):
    recipient: str
    message: str


# ---------------- HEALTH CHECK ----------------

@app.get("/")
def home():
    return {
        "system": "RYT Football Academy AI",
        "status": "running"
    }


# ---------------- AI AGENT ROUTING ----------------

@app.post("/chat")
def chat(request: ChatRequest):
    task = Task(user_input=request.message)
    result = agent.route_task(task)
    return result


# ---------------- NPO ENDPOINTS ----------------

@app.post("/npo/director/add")
def add_director(name: str, id_number: Optional[str] = None, role: Optional[str] = None):
    return npo.add_director(name, id_number, role)


@app.post("/npo/member/add")
def add_member(name: str):
    return npo.add_member(name)


@app.get("/npo/compliance")
def check_compliance():
    return npo.check_compliance()


@app.get("/npo/funding-score")
def funding_score():
    return npo.funding_readiness_score()


# ---------------- SPONSOR ENDPOINTS ----------------

@app.post("/sponsors/add")
def add_sponsor(lead: SponsorLeadRequest):
    return sponsors.add_lead(
        name=lead.name,
        industry=lead.industry,
        email=lead.email,
        phone=lead.phone
    )


@app.get("/sponsors/pipeline")
def sponsor_pipeline():
    return sponsors.pipeline_summary()


# ---------------- WHATSAPP ENDPOINTS ----------------

@app.post("/whatsapp/send")
def send_message(request: WhatsAppRequest):
    return whatsapp.send_message(request.recipient, request.message)


@app.post("/whatsapp/bulk")
def send_bulk(recipients: List[str], message: str):
    return whatsapp.send_bulk(recipients, message)


@app.get("/whatsapp/status")
def whatsapp_status():
    return whatsapp.queue_status()


# ---------------- RUN SERVER ----------------
# To run locally:
# uvicorn api.server:app --reload
