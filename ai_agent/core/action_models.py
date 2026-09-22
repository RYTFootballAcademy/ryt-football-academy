"""Persistent approval queue for FAOS agent actions."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text

from ai_agent.modules.database import Base


class AgentTask(Base):
    """One proposed agent action with approval and execution audit fields."""

    __tablename__ = "agent_tasks"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    title = Column(String, nullable=False)
    module = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    payload_json = Column(Text, default="{}")
    priority = Column(String, default="Normal")
    status = Column(String, default="Awaiting Approval")
    requires_approval = Column(Boolean, default=True)

    created_at = Column(String, nullable=False)
    approved_at = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)
    rejected_at = Column(String, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    executed_at = Column(String, nullable=True)
    result_json = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
