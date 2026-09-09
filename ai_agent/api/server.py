"""RYT Football Academy Operating System (FAOS) API entry point."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ai_agent.core.agent import RYTAI_Agent, Task
from ai_agent.crm.api import router as crm_router
from ai_agent.faos.api import router as faos_router
from ai_agent.modules.database import engine, init_db
from ai_agent.modules.funding_finder import FundingFinder
from ai_agent.modules.npo_compliance import NPOComplianceTracker
from ai_agent.modules.proposal_generator import ProposalGenerator
from ai_agent.modules.whatsapp_hub import WhatsAppHub


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.applied_migrations = init_db()
    yield


app = FastAPI(
    title="RYT Football Academy Operating System",
    description=(
        "FAOS backend for academy operations, player development, CRM, finance, "
        "sponsorship, governance, camps, commerce and AI-assisted workflows."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

origins = [
    value.strip()
    for value in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000",
    ).split(",")
    if value.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(crm_router)
app.include_router(faos_router)

agent = RYTAI_Agent()
proposal_generator = ProposalGenerator()
funding_finder = FundingFinder()
npo_tracker = NPOComplianceTracker()
whatsapp_hub = WhatsAppHub()


class ChatRequest(BaseModel):
    message: str


class WhatsAppRequest(BaseModel):
    recipient: str
    message: str
    message_type: str = "text"


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "service": "RYT Football Academy FAOS",
        "version": app.version,
        "database": engine.dialect.name,
    }


@app.post("/chat", tags=["AI"])
def chat(payload: ChatRequest):
    return agent.route_task(Task(user_input=payload.message))


@app.post("/whatsapp/send", tags=["Communication"])
def queue_whatsapp(payload: WhatsAppRequest):
    return whatsapp_hub.send_message(
        payload.recipient,
        payload.message,
        payload.message_type,
    )


@app.get("/whatsapp/queue", tags=["Communication"])
def whatsapp_queue_status():
    return whatsapp_hub.queue_status()


@app.post("/proposal/generate", tags=["Tools"])
def generate_proposal(sponsor_name: str, contribution_amount: float):
    return proposal_generator.generate_proposal(sponsor_name, contribution_amount)


@app.post("/funding/add", tags=["Tools"])
def add_opportunity(category: str, name: str, description: str, contact: str):
    return funding_finder.add_opportunity(category, name, description, contact)


@app.get("/funding/list", tags=["Tools"])
def list_opportunities():
    return funding_finder.list_opportunities()


@app.get("/funding/category/{category}", tags=["Tools"])
def find_by_category(category: str):
    return funding_finder.find_by_category(category)


@app.post("/npo/director/add", tags=["NPO Tools"])
def add_director(name: str):
    return npo_tracker.add_director(name)


@app.post("/npo/member/add", tags=["NPO Tools"])
def add_member(name: str):
    return npo_tracker.add_member(name)


@app.post("/npo/meeting/record", tags=["NPO Tools"])
def record_meeting(date: str, attendees: List[str]):
    return npo_tracker.record_meeting(date, attendees)


@app.put("/npo/director/inactive", tags=["NPO Tools"])
def mark_inactive_director(name: str):
    return npo_tracker.mark_inactive_director(name)


@app.post("/npo/task/add", tags=["NPO Tools"])
def add_task(task: str, due_date: str):
    return npo_tracker.add_task(task, due_date)


@app.put("/npo/task/complete", tags=["NPO Tools"])
def complete_task(task: str):
    return npo_tracker.complete_task(task)


@app.get("/npo/tasks", tags=["NPO Tools"])
def list_tasks():
    return npo_tracker.list_tasks()


ROOT_DIR = Path(__file__).resolve().parents[2]
DASHBOARD_DIR = ROOT_DIR / "dashboard"
if DASHBOARD_DIR.exists():
    app.mount("/dashboard", StaticFiles(directory=DASHBOARD_DIR, html=True), name="dashboard")


@app.get("/", include_in_schema=False)
def root():
    if DASHBOARD_DIR.exists():
        return RedirectResponse(url="/dashboard/")
    return {"service": "RYT Football Academy FAOS", "docs": "/docs"}
