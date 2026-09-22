"""Company-governance and regulator-specific workflow records for FAOS."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text

from ai_agent.modules.database import Base


class BeneficialOwnershipFiling(Base):
    """Track CIPC beneficial-ownership declarations and supporting register status."""

    __tablename__ = "beneficial_ownership_filings"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    reporting_period = Column(String, nullable=True)
    declaration_date = Column(String, nullable=True)
    status = Column(String, default="Draft")
    reference = Column(String, nullable=True)
    security_register_status = Column(String, nullable=True)
    notes = Column(Text, nullable=True)


class CompanyFinancialFiling(Base):
    """Track the AFS/FAS component associated with CIPC annual-return compliance."""

    __tablename__ = "company_financial_filings"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    reporting_period = Column(String, nullable=True)
    filing_basis = Column(String, nullable=True)  # AFS, FAS or To Verify
    due_date = Column(String, nullable=True)
    filed_date = Column(String, nullable=True)
    status = Column(String, default="Draft")
    reference = Column(String, nullable=True)
    notes = Column(Text, nullable=True)


class DSDAnnualReport(Base):
    """Detailed tracker for the DSD NPO annual-report package."""

    __tablename__ = "dsd_annual_reports"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    reporting_period = Column(String, nullable=False)
    due_date = Column(String, nullable=True)
    narrative_status = Column(String, default="Missing")
    financial_statement_status = Column(String, default="Missing")
    accounting_officer_report_status = Column(String, default="Missing")
    bank_statement_status = Column(String, nullable=True)
    affidavit_status = Column(String, nullable=True)
    submitted_date = Column(String, nullable=True)
    status = Column(String, default="Draft")
    reference = Column(String, nullable=True)
    notes = Column(Text, nullable=True)


class DirectorChangeCase(Base):
    """Approval and regulator-confirmation workflow for CIPC director changes.

    A case never changes the verified director register merely because it is
    drafted or filed. Register/history updates only occur after an explicit
    regulator-confirmation step.
    """

    __tablename__ = "director_change_cases"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    change_type = Column(String, nullable=False)  # Appointment/Resignation/Removal/Replacement
    outgoing_director_id = Column(Integer, ForeignKey("directors.id"), nullable=True)
    incoming_first_name = Column(String, nullable=True)
    incoming_last_name = Column(String, nullable=True)
    incoming_role = Column(String, nullable=True)
    incoming_director_id = Column(Integer, ForeignKey("directors.id"), nullable=True)

    meeting_date = Column(String, nullable=True)
    resolution_date = Column(String, nullable=True)
    resolution_reference = Column(String, nullable=True)

    status = Column(String, default="Draft")
    filed_date = Column(String, nullable=True)
    cipc_reference = Column(String, nullable=True)
    confirmed_date = Column(String, nullable=True)
    effective_date = Column(String, nullable=True)
    notes = Column(Text, nullable=True)


class ExternalPortalWorkflow(Base):
    """Local-only orchestration metadata for regulated portal workflows.

    Authentication secrets, OTPs, card details, cookies and security answers are
    deliberately excluded. The user enters those directly into the browser.
    """

    __tablename__ = "external_portal_workflows"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    service = Column(String, nullable=False)
    workflow_type = Column(String, nullable=False)
    registration_number = Column(String, nullable=True)
    status = Column(String, default="Prepared")
    current_step = Column(String, nullable=True)
    requires_user_login = Column(Boolean, default=True)
    requires_user_approval = Column(Boolean, default=True)
    created_at = Column(String, nullable=False)
    started_at = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)
    completed_at = Column(String, nullable=True)
    process_id = Column(Integer, nullable=True)
    external_reference = Column(String, nullable=True)
    last_url = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)


class ExternalPortalWorkflowEvent(Base):
    """Non-secret audit events emitted by a portal automation run."""

    __tablename__ = "external_portal_workflow_events"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("external_portal_workflows.id"), nullable=False)
    event_time = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    page_url = Column(Text, nullable=True)
