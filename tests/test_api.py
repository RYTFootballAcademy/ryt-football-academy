"""End-to-end smoke tests for the FAOS backend."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB = Path(__file__).with_name("test_academy.db").resolve()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ.pop("FAOS_API_KEY", None)

from ai_agent.api.server import app  # noqa: E402
from ai_agent.modules.database import engine  # noqa: E402


@pytest.fixture(scope="module")
def client():
    engine.dispose()
    if TEST_DB.exists():
        TEST_DB.unlink()

    with TestClient(app) as test_client:
        yield test_client

    # SQLite files remain locked on Windows while pooled connections are open.
    # Dispose the engine before deleting the temporary test database.
    engine.dispose()
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
        "external_portal_accounts",
        "player_intake_status",
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


def test_agent_approval_workflow(client: TestClient):
    prepared = client.post(
        "/agent/prepare",
        json={
            "instruction": "Create a compliance task to verify our CIPC status",
            "organization_id": 1,
            "priority": "High",
        },
    )
    assert prepared.status_code == 201, prepared.text
    task = prepared.json()
    assert task["status"] == "Awaiting Approval"
    assert task["action_type"] == "create_compliance_task"
    assert task["requires_approval"] is True

    hidden = client.get("/faos/agent_tasks")
    assert hidden.status_code == 404

    approved = client.post(
        f"/agent/tasks/{task['id']}/approve",
        json={"approved_by": "Founder"},
    )
    assert approved.status_code == 200, approved.text
    completed = approved.json()
    assert completed["status"] == "Completed"
    assert completed["result"]["resource"] == "compliance_tasks"

    compliance = client.get("/crm/compliance")
    assert compliance.status_code == 200
    assert any("CIPC" in item["title"] for item in compliance.json())

    rejected_task = client.post(
        "/agent/prepare",
        json={"instruction": "Prepare a parent message about emergency contact information"},
    )
    assert rejected_task.status_code == 201
    rejected = client.post(
        f"/agent/tasks/{rejected_task.json()['id']}/reject",
        json={"reason": "Not needed today"},
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "Rejected"

    report_task = client.post(
        "/agent/prepare",
        json={"instruction": "Generate a monthly management report"},
    )
    assert report_task.status_code == 201
    report_approved = client.post(
        f"/agent/tasks/{report_task.json()['id']}/approve",
        json={"approved_by": "Founder"},
    )
    assert report_approved.status_code == 200
    assert report_approved.json()["result"]["resource"] == "generated_reports"

    summary = client.get("/agent/summary")
    assert summary.status_code == 200
    assert summary.json()["completed"] >= 2
    assert summary.json()["rejected"] >= 1


def test_player_guardian_intake_and_readiness(client: TestClient):
    team = client.post(
        "/faos/teams",
        json={
            "organization_id": 1,
            "name": "RYT U15",
            "age_group": "U15",
            "season": "2026",
        },
    )
    assert team.status_code == 201, team.text
    team_id = team.json()["id"]

    intake = client.post(
        "/crm/intake/player",
        json={
            "organization_id": 1,
            "player": {
                "name": "Intake Test Player",
                "age": 14,
                "dob": "2012-02-10",
                "team_id": team_id,
                "position": "Midfielder",
                "school": "Test Secondary",
                "grade": "8",
                "allergies": "None known",
                "injuries": "None known",
                "medication": "None",
            },
            "guardian": {
                "name": "Intake Test Guardian",
                "phone": "0711111111",
                "whatsapp": "0711111111",
                "email": "intake-parent@example.com",
                "relationship_to_player": "Parent",
                "emergency_contact_name": "Backup Guardian",
                "emergency_contact_phone": "0722222222",
                "emergency_contact_relationship": "Relative",
            },
            "forms": {
                "registration_form_status": "Signed",
                "medical_form_status": "Signed",
                "emergency_contact_form_status": "Signed",
                "media_consent_status": "Signed",
                "indemnity_form_status": "Signed",
                "medical_info_confirmed": True,
            },
        },
    )
    assert intake.status_code == 201, intake.text
    result = intake.json()
    assert result["player_id"] > 0
    assert result["parent_id"] > 0
    assert result["team_id"] == team_id

    readiness = client.get("/crm/intake/readiness?organization_id=1")
    assert readiness.status_code == 200, readiness.text
    record = next(
        item
        for item in readiness.json()["records"]
        if item["player_id"] == result["player_id"]
    )
    assert record["complete"] is True
    assert record["completeness_percent"] == 100
    assert record["missing"] == []

    duplicate = client.post(
        "/crm/intake/player",
        json={
            "organization_id": 1,
            "player": {
                "name": "Intake Test Player",
                "dob": "2012-02-10",
                "team_id": team_id,
            },
            "guardian": {
                "name": "Intake Test Guardian",
                "phone": "0711111111",
            },
        },
    )
    assert duplicate.status_code == 422


def test_bulk_player_intake_reuses_guardian(client: TestClient):
    teams = client.get("/faos/teams")
    assert teams.status_code == 200
    team_id = teams.json()[0]["id"]

    bulk = client.post(
        "/crm/intake/bulk",
        json={
            "records": [
                {
                    "organization_id": 1,
                    "player": {
                        "name": "Bulk Player One",
                        "age": 13,
                        "team_id": team_id,
                        "school": "Bulk School",
                        "grade": "7",
                    },
                    "guardian": {
                        "name": "Shared Guardian",
                        "phone": "0733333333",
                        "whatsapp": "0733333333",
                        "relationship_to_player": "Parent",
                    },
                },
                {
                    "organization_id": 1,
                    "player": {
                        "name": "Bulk Player Two",
                        "age": 14,
                        "team_id": team_id,
                        "school": "Bulk School",
                        "grade": "8",
                    },
                    "guardian": {
                        "name": "Shared Guardian",
                        "phone": "0733333333",
                        "whatsapp": "0733333333",
                        "relationship_to_player": "Parent",
                    },
                },
            ]
        },
    )
    assert bulk.status_code == 201, bulk.text
    payload = bulk.json()
    assert payload["created_count"] == 2
    assert payload["error_count"] == 0
    assert payload["created"][0]["parent_id"] == payload["created"][1]["parent_id"]


def test_company_compliance_and_director_change_workflow(client: TestClient):
    profile = client.post(
        "/faos/npo_regulatory_profiles",
        json={
            "organization_id": 1,
            "legal_name": "Test Legal Entity",
            "trading_name": "RYT Test",
            "cipc_registration_number": "K2021000000",
            "incorporation_date": "2021-10-25",
            "financial_year_end": "31 October",
        },
    )
    assert profile.status_code in (201, 400), profile.text

    outgoing = client.post(
        "/faos/directors",
        json={
            "organization_id": 1,
            "first_name": "Historical",
            "last_name": "Director",
            "role": "Director",
            "status": "Historical - current status unverified",
        },
    )
    assert outgoing.status_code == 201, outgoing.text
    outgoing_id = outgoing.json()["id"]

    history = client.post(
        "/faos/director_appointment_history",
        json={
            "organization_id": 1,
            "director_id": outgoing_id,
            "appointment_date": "2021-10-25",
            "appointment_source": "CIPC COR 14.1A",
            "status": "Historical - current status unverified",
        },
    )
    assert history.status_code == 201, history.text

    prepared = client.post(
        "/agent/tasks",
        json={
            "title": "Prepare director replacement",
            "module": "company",
            "action_type": "prepare_director_change",
            "organization_id": 1,
            "priority": "High",
            "payload": {
                "change_type": "Replacement",
                "outgoing_director_id": outgoing_id,
                "incoming_first_name": "New",
                "incoming_last_name": "Director",
                "incoming_role": "Director",
                "resolution_date": "2026-09-22",
                "resolution_reference": "Board Resolution TEST-01",
            },
        },
    )
    assert prepared.status_code == 201, prepared.text
    approved = client.post(
        f"/agent/tasks/{prepared.json()['id']}/approve",
        json={"approved_by": "Founder"},
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "Completed"
    case_id = approved.json()["result"]["record_id"]

    hidden = client.get("/faos/director_change_cases")
    assert hidden.status_code == 404

    ready = client.post(f"/company/director-changes/{case_id}/ready")
    assert ready.status_code == 200, ready.text
    assert ready.json()["status"] == "Ready to File"

    filed = client.post(
        f"/company/director-changes/{case_id}/filed",
        json={"filed_date": "2026-09-22", "cipc_reference": "CIPC-TEST-001"},
    )
    assert filed.status_code == 200, filed.text
    assert filed.json()["status"] == "Filed - Awaiting CIPC Confirmation"

    confirmed = client.post(
        f"/company/director-changes/{case_id}/confirm",
        json={
            "confirmed_date": "2026-09-23",
            "effective_date": "2026-09-23",
            "cipc_reference": "CIPC-TEST-001",
        },
    )
    assert confirmed.status_code == 200, confirmed.text
    assert confirmed.json()["status"] == "Confirmed"
    assert confirmed.json()["incoming_director_id"] is not None

    directors = client.get("/faos/directors")
    assert directors.status_code == 200
    old = next(item for item in directors.json() if item["id"] == outgoing_id)
    new = next(
        item
        for item in directors.json()
        if item["id"] == confirmed.json()["incoming_director_id"]
    )
    assert "Historical" in old["status"]
    assert new["status"] == "Active - CIPC verified"

    annual = client.post(
        "/agent/tasks",
        json={
            "title": "Track CIPC Annual Return 2026",
            "module": "company",
            "action_type": "record_regulatory_filing",
            "organization_id": 1,
            "payload": {
                "regulator": "CIPC",
                "filing_type": "Annual Return",
                "reporting_period": "2026",
                "status": "Pending",
            },
        },
    )
    assert annual.status_code == 201
    annual_done = client.post(
        f"/agent/tasks/{annual.json()['id']}/approve",
        json={"approved_by": "Founder"},
    )
    assert annual_done.status_code == 200
    assert annual_done.json()["result"]["resource"] == "regulatory_filings"

    bo = client.post(
        "/agent/tasks",
        json={
            "title": "Track beneficial ownership 2026",
            "module": "company",
            "action_type": "record_beneficial_ownership",
            "organization_id": 1,
            "payload": {"reporting_period": "2026", "status": "Draft"},
        },
    )
    assert bo.status_code == 201
    bo_done = client.post(
        f"/agent/tasks/{bo.json()['id']}/approve",
        json={"approved_by": "Founder"},
    )
    assert bo_done.status_code == 200
    assert bo_done.json()["result"]["resource"] == "beneficial_ownership_filings"

    financial = client.post(
        "/agent/tasks",
        json={
            "title": "Track FAS 2026",
            "module": "company",
            "action_type": "record_company_financial_filing",
            "organization_id": 1,
            "payload": {
                "reporting_period": "2026",
                "filing_basis": "FAS",
                "status": "Draft",
            },
        },
    )
    assert financial.status_code == 201
    financial_done = client.post(
        f"/agent/tasks/{financial.json()['id']}/approve",
        json={"approved_by": "Founder"},
    )
    assert financial_done.status_code == 200

    dsd = client.post(
        "/agent/tasks",
        json={
            "title": "Prepare DSD annual report 2025",
            "module": "company",
            "action_type": "prepare_dsd_annual_report",
            "organization_id": 1,
            "payload": {
                "reporting_period": "FY ended 2025-10-31",
                "due_date": "2026-07-31",
            },
        },
    )
    assert dsd.status_code == 201
    dsd_done = client.post(
        f"/agent/tasks/{dsd.json()['id']}/approve",
        json={"approved_by": "Founder"},
    )
    assert dsd_done.status_code == 200
    assert dsd_done.json()["result"]["resource"] == "dsd_annual_reports"

    dashboard = client.get("/company/dashboard?organization_id=1")
    assert dashboard.status_code == 200, dashboard.text
    data = dashboard.json()
    assert len(data["cipc_annual_returns"]) >= 1
    assert len(data["beneficial_ownership"]) >= 1
    assert len(data["company_financial_filings"]) >= 1
    assert len(data["dsd_annual_reports"]) >= 1
    assert len(data["director_changes"]) >= 1
