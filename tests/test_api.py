"""End-to-end smoke tests for the FAOS backend."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB = Path(__file__).with_name("test_academy.db").resolve()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ.pop("FAOS_API_KEY", None)

from ai_agent.api.server import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    if TEST_DB.exists():
        TEST_DB.unlink()
    with TestClient(app) as test_client:
        yield test_client
    if TEST_DB.exists():
        TEST_DB.unlink()


def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_full_faos_resource_registry(client: TestClient):
    response = client.get("/faos/resources")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] >= 50
    for required in [
        "organizations",
        "teams",
        "players",
        "sponsors",
        "expenses",
        "directors",
        "orders",
        "ai_conversations",
    ]:
        assert required in payload["resources"]


def test_extended_resource_crud(client: TestClient):
    created = client.post(
        "/faos/organizations",
        json={
            "name": "Roshunville Young Tigers Sports Academy",
            "town": "Schweizer-Reneke",
            "province": "North West",
            "country": "South Africa",
            "status": "Active",
        },
    )
    assert created.status_code == 201, created.text
    organization_id = created.json()["id"]

    fetched = client.get(f"/faos/organizations/{organization_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Roshunville Young Tigers Sports Academy"


def test_core_crm_flow(client: TestClient):
    parent = client.post(
        "/crm/parents",
        json={"name": "Test Parent", "phone": "0100000000", "email": "parent@example.com"},
    )
    assert parent.status_code == 201, parent.text

    player = client.post(
        "/crm/players",
        json={
            "name": "Test Player",
            "age": 14,
            "position": "Midfielder",
            "parent_id": parent.json()["id"],
        },
    )
    assert player.status_code == 201, player.text
    player_id = player.json()["id"]

    fee = client.post(
        "/crm/fees",
        json={"player_id": player_id, "amount": 150, "status": "Paid", "due_date": "2026-09-30"},
    )
    assert fee.status_code == 201, fee.text
    assert fee.json()["due_date"] == "2026-09-30"

    trial = client.post(
        "/crm/trials",
        json={
            "player_id": player_id,
            "date": "2026-09-09",
            "result": "Passed",
            "notes": "API smoke test",
        },
    )
    assert trial.status_code == 201, trial.text
    assert trial.json()["notes"] == "API smoke test"


def test_sponsor_persistence_and_crud(client: TestClient):
    response = client.post(
        "/crm/sponsors",
        json={
            "name": "FAOS Test Sponsor",
            "industry": "Sports",
            "contact_person": "Test Contact",
            "email": "sponsor@example.com",
            "phone": "0112223333",
        },
    )
    assert response.status_code == 201, response.text
    sponsor_id = response.json()["id"]
    assert response.json()["status"] == "Prospect"

    listing = client.get("/crm/sponsors")
    assert listing.status_code == 200
    assert any(item["id"] == sponsor_id for item in listing.json())

    updated = client.patch(
        f"/crm/sponsors/{sponsor_id}/status",
        json={"status": "Active"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "Active"

    deleted = client.delete(f"/crm/sponsors/{sponsor_id}")
    assert deleted.status_code == 204


def test_decision_router_and_whatsapp_queue(client: TestClient):
    routed = client.post("/chat", json={"message": "We need sponsors for new kits"})
    assert routed.status_code == 200
    payload = routed.json()
    assert payload["module"] == "sponsor"
    assert payload["action"] == "build_pipeline"
    assert "/crm/sponsors" in payload["relevant_endpoints"]

    queued = client.post(
        "/whatsapp/send",
        json={"recipient": "+27000000000", "message": "Training update"},
    )
    assert queued.status_code == 200
    assert queued.json()["status"] == "queued"

    queue = client.get("/whatsapp/queue")
    assert queue.status_code == 200
    assert queue.json()["queued"] >= 1


def test_summary_and_dashboard(client: TestClient):
    summary = client.get("/crm/summary")
    assert summary.status_code == 200
    assert summary.json()["players"] >= 1
    assert summary.json()["parents"] >= 1

    dashboard = client.get("/dashboard/")
    assert dashboard.status_code == 200
    assert "FAOS" in dashboard.text
