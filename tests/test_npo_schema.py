"""Schema coverage for South African NPO/NPC governance records."""

from ai_agent.modules.database import Base, _load_models


def test_npo_governance_tables_are_registered():
    _load_models()
    required = {
        "npo_regulatory_profiles",
        "director_appointment_history",
        "regulatory_filings",
        "governance_documents",
    }
    assert required.issubset(Base.metadata.tables)


def test_npo_regulatory_profile_has_required_fields():
    _load_models()
    columns = set(Base.metadata.tables["npo_regulatory_profiles"].columns.keys())
    expected = {
        "organization_id",
        "legal_name",
        "trading_name",
        "entity_type",
        "cipc_registration_number",
        "cipc_status",
        "incorporation_date",
        "dsd_npo_number",
        "dsd_registration_date",
        "dsd_status",
        "financial_year_end",
        "sars_income_tax_number",
        "pbo_number",
        "tax_exemption_status",
        "physical_address",
        "postal_address",
        "notes",
    }
    assert expected.issubset(columns)


def test_director_history_and_filing_fields():
    _load_models()
    director_columns = set(
        Base.metadata.tables["director_appointment_history"].columns.keys()
    )
    assert {
        "organization_id",
        "director_id",
        "appointment_date",
        "resignation_date",
        "appointment_source",
        "appointment_reference",
        "status",
        "notes",
    }.issubset(director_columns)

    filing_columns = set(Base.metadata.tables["regulatory_filings"].columns.keys())
    assert {
        "organization_id",
        "regulator",
        "filing_type",
        "reporting_period",
        "due_date",
        "filed_date",
        "status",
        "reference",
        "notes",
    }.issubset(filing_columns)
