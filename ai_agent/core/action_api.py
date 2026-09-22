"""Approval-gated API for FAOS agent actions."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ai_agent.core.action_models import AgentTask
from ai_agent.core.action_service import (
    create_task,
    execute_task,
    prepare_from_instruction,
    serialize_task,
    utc_now,
)
from ai_agent.core.agent import RYTAI_Agent
from ai_agent.modules.database import get_db


router = APIRouter(prefix="/agent", tags=["AI Agent Actions"])
_agent = RYTAI_Agent()


class PrepareRequest(BaseModel):
    instruction: str
    organization_id: int | None = 1
    priority: str = "Normal"


class TaskCreateRequest(BaseModel):
    title: str
    module: str
    action_type: str
    description: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    organization_id: int | None = 1
    priority: str = "Normal"


class ApprovalRequest(BaseModel):
    approved_by: str = "Founder"


class RejectionRequest(BaseModel):
    reason: str | None = None


@router.post("/prepare", status_code=status.HTTP_201_CREATED)
def prepare_action(payload: PrepareRequest, db: Session = Depends(get_db)):
    try:
        task = prepare_from_instruction(
            db,
            _agent,
            payload.instruction,
            organization_id=payload.organization_id,
            priority=payload.priority,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return serialize_task(task)


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_structured_action(payload: TaskCreateRequest, db: Session = Depends(get_db)):
    try:
        task = create_task(
            db,
            title=payload.title,
            module=payload.module,
            action_type=payload.action_type,
            description=payload.description,
            payload=payload.payload,
            organization_id=payload.organization_id,
            priority=payload.priority,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return serialize_task(task)


@router.get("/tasks")
def list_actions(
    task_status: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(AgentTask)
    if task_status:
        query = query.filter(AgentTask.status == task_status)
    tasks = query.order_by(AgentTask.id.desc()).limit(limit).all()
    return [serialize_task(task) for task in tasks]


@router.get("/summary")
def action_summary(db: Session = Depends(get_db)):
    statuses = [
        "Awaiting Approval",
        "Approved",
        "Executing",
        "Completed",
        "Rejected",
        "Failed",
    ]
    counts = {
        item: db.query(AgentTask).filter(AgentTask.status == item).count()
        for item in statuses
    }
    return {
        "total": db.query(AgentTask).count(),
        "awaiting_approval": counts["Awaiting Approval"],
        "approved": counts["Approved"],
        "executing": counts["Executing"],
        "completed": counts["Completed"],
        "rejected": counts["Rejected"],
        "failed": counts["Failed"],
    }


@router.get("/tasks/{task_id}")
def get_action(task_id: int, db: Session = Depends(get_db)):
    task = db.get(AgentTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Agent task not found")
    return serialize_task(task)


@router.post("/tasks/{task_id}/approve")
def approve_action(
    task_id: int,
    payload: ApprovalRequest,
    db: Session = Depends(get_db),
):
    task = db.get(AgentTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Agent task not found")
    if task.status != "Awaiting Approval":
        raise HTTPException(
            status_code=409,
            detail=f"Task cannot be approved from status: {task.status}",
        )

    task.status = "Approved"
    task.approved_at = utc_now()
    task.approved_by = payload.approved_by
    db.commit()
    db.refresh(task)

    task = execute_task(db, task)
    return serialize_task(task)


@router.post("/tasks/{task_id}/reject")
def reject_action(
    task_id: int,
    payload: RejectionRequest,
    db: Session = Depends(get_db),
):
    task = db.get(AgentTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Agent task not found")
    if task.status != "Awaiting Approval":
        raise HTTPException(
            status_code=409,
            detail=f"Task cannot be rejected from status: {task.status}",
        )

    task.status = "Rejected"
    task.rejected_at = utc_now()
    task.rejection_reason = payload.reason
    db.commit()
    db.refresh(task)
    return serialize_task(task)
