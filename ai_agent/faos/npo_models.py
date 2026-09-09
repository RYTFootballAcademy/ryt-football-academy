"""South African NPO/NPC governance and regulatory records for FAOS.

These models complement the core academy Organization/Director/Member models.
They deliberately keep regulatory history separate from day-to-day academy data
so DSD, CIPC and SARS records can be tracked without overwriting operational
names or historical registrations.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text

from ai_agent.modules.database import Base


class NPORegulatoryProfile(Base):
    """One regulatory master profile per FAOS organization."""

    __tablename__ = "npo_regulatory_profiles"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=False,
        unique=True,
    )
    legal_name = Column(String, nullable=True)
    trading_name = Column(String, nullable=True)
    entity_type = Column(String, nullable=True)

    # CIPC / Companies Act registration details.
    cipc_registration_number = Column(String, nullable=True)
    cipc_status = Column(String, nullable=True)
    incorporation_date = Column(String, nullable=True)

    # Department of Social Development NPO registration details.
    dsd_npo_number = Column(String, nullable=True)
    dsd_registration_date = Column(String, nullable=True)
    dsd_status = Column(String, nullable=True)

    # Financial and SARS/PBO compliance metadata.
    financial_year_end = Column(String, nullable=True)
    sars_income_tax_number = Column(String, nullable=True)
    pbo_number = Column(String, nullable=True)
    tax_exemption_status = Column(String, nullable=True)

    physical_address = Column(Text, nullable=True)
    postal_address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)


class DirectorAppointmentHistory(Base):
    """Track appointments/resignations without overwriting a Director record."""

    __tablename__ = "director_appointment_history"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    director_id = Column(Integer, ForeignKey("directors.id"), nullable=True)
    appointment_date = Column(String, nullable=True)
    resignation_date = Column(String, nullable=True)
    appointment_source = Column(String, nullable=True)
    appointment_reference = Column(String, nullable=True)
    status = Column(String, default="Active")
    notes = Column(Text, nullable=True)


class RegulatoryFiling(Base):
    """DSD, CIPC, SARS and other recurring filing/compliance history."""

    __tablename__ = "regulatory_filings"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    regulator = Column(String, nullable=False)
    filing_type = Column(String, nullable=False)
    reporting_period = Column(String, nullable=True)
    due_date = Column(String, nullable=True)
    filed_date = Column(String, nullable=True)
    status = Column(String, default="Pending")
    reference = Column(String, nullable=True)
    notes = Column(Text, nullable=True)


class GovernanceDocument(Base):
    """Register constitutions, certificates, minutes, resolutions and evidence."""

    __tablename__ = "governance_documents"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    document_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    version = Column(String, nullable=True)
    document_date = Column(String, nullable=True)
    effective_date = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    status = Column(String, default="Current")
    notes = Column(Text, nullable=True)
