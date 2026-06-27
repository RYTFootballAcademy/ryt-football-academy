from sqlalchemy import Column, Integer, String, ForeignKey
from ai_agent.modules.database import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    position = Column(String)
    parent_id = Column(Integer, ForeignKey("parents.id"))

class Parent(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String)
    email = Column(String)

class Coach(Base):
    __tablename__ = "coaches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(String)   # e.g., Head Coach, Assistant
    phone = Column(String)
    email = Column(String)

class Sponsor(Base):
    __tablename__ = "sponsors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    industry = Column(String)
    contact_person = Column(String)
    email = Column(String)
    phone = Column(String)

class FundingOpportunity(Base):
    __tablename__ = "funding_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    amount = Column(Integer)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"))

class ComplianceTask(Base):
    __tablename__ = "compliance_tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    due_date = Column(String)   # store as ISO string
    status = Column(String)     # Pending, Completed, Overdue

class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"))
    funding_id = Column(Integer, ForeignKey("funding_opportunities.id"))
    status = Column(String)   # Draft, Submitted, Approved, Rejected

class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    start_date = Column(String)   # ISO string
    end_date = Column(String)




