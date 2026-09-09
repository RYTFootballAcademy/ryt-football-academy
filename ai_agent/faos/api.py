"""Generic administration API for the full FAOS data model.

Core day-to-day workflows have typed routes under ``/crm``. The ``/faos`` API
provides controlled CRUD access to every mapped resource in the database
specification, making the remaining modules usable without writing dozens of
nearly identical route files.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import Session

from ai_agent.modules.database import Base, get_db
from ai_agent.crm import models as _crm_models  # noqa: F401
from ai_agent.faos import models as _faos_models  # noqa: F401

router = APIRouter(prefix="/faos", tags=["FAOS Admin"])


def _require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    expected = os.getenv("FAOS_API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


def _resources() -> dict[str, type]:
    return {
        mapper.class_.__tablename__: mapper.class_
        for mapper in Base.registry.mappers
        if hasattr(mapper.class_, "__tablename__")
    }


def _model_for(resource: str) -> type:
    model = _resources().get(resource)
    if model is None:
        raise HTTPException(status_code=404, detail=f"Unknown FAOS resource: {resource}")
    return model


def _serialize(instance: Any) -> dict[str, Any]:
    mapper = sa_inspect(instance).mapper
    return {attribute.key: getattr(instance, attribute.key) for attribute in mapper.column_attrs}


def _clean_payload(model: type, payload: dict[str, Any], *, partial: bool = False) -> dict[str, Any]:
    allowed = {column.name for column in model.__table__.columns if column.name != "id"}
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise HTTPException(status_code=422, detail={"unknown_fields": unknown})
    if not partial and not payload:
        raise HTTPException(status_code=422, detail="Payload cannot be empty")
    return {key: value for key, value in payload.items() if key in allowed}


@router.get("/resources")
def list_resources():
    resources = _resources()
    return {
        "count": len(resources),
        "resources": sorted(resources),
        "write_protection": "X-API-Key required when FAOS_API_KEY is configured",
    }


@router.get("/{resource}")
def list_resource_records(
    resource: str,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    model = _model_for(resource)
    records = db.query(model).order_by(model.id.desc()).offset(offset).limit(limit).all()
    return [_serialize(record) for record in records]


@router.post("/{resource}", status_code=status.HTTP_201_CREATED, dependencies=[Depends(_require_api_key)])
def create_resource_record(
    resource: str,
    payload: dict[str, Any],
    db: Session = Depends(get_db),
):
    model = _model_for(resource)
    values = _clean_payload(model, payload)
    record = model(**values)
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except (IntegrityError, StatementError) as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc.orig if hasattr(exc, "orig") else exc)) from exc
    return _serialize(record)


@router.get("/{resource}/{record_id}")
def get_resource_record(resource: str, record_id: int, db: Session = Depends(get_db)):
    model = _model_for(resource)
    record = db.get(model, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return _serialize(record)


@router.patch("/{resource}/{record_id}", dependencies=[Depends(_require_api_key)])
def update_resource_record(
    resource: str,
    record_id: int,
    payload: dict[str, Any],
    db: Session = Depends(get_db),
):
    model = _model_for(resource)
    record = db.get(model, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    values = _clean_payload(model, payload, partial=True)
    for key, value in values.items():
        setattr(record, key, value)
    try:
        db.commit()
        db.refresh(record)
    except (IntegrityError, StatementError) as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc.orig if hasattr(exc, "orig") else exc)) from exc
    return _serialize(record)


@router.delete("/{resource}/{record_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(_require_api_key)])
def delete_resource_record(resource: str, record_id: int, db: Session = Depends(get_db)):
    model = _model_for(resource)
    record = db.get(model, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
