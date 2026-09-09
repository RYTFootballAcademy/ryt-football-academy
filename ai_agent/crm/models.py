"""Core CRM models used by the RYT Football Academy Operating System (FAOS).

These models intentionally retain the original MVP field names while adding the
fields required by the repository's database specification. This keeps existing
SQLite data and API clients compatible while allowing the system to grow.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text

from ai_agent.modules.database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    name = Column(String, index=True, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    preferred_name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    dob = Column(String, nullable=True)
    position = Column(String, nullable=True)
    primary_position = Column(String, nullable=True)
    secondary_position = Column(String, nullable=True)
    preferred_foot = Column(String, nullable=True)
    registration_date = Column(String, nullable=True)
    status = Column(String, default="Active")
    squad_number = Column(Integer, nullable=True)
    allergies = Column(Text, nullable=True)
    injuries = Column(Text, nullable=True)
    medication = Column(Text, nullable=True)
    school = Column(String, nullable=True)
    grade = Column(String, nullable=True)
    profile_photo = Column(String, nullable=True)
    id_number = Column(String, nullable=True)
    notes = Column(Text, nullable=True)


class Parent(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    name = Column(String, index=True, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    whatsapp = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact = Column(String, nullable=True)
    relationship_to_player = Column(String, nullable=True)


class Coach(Base):
    __tablename__ = "coaches"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    name = Column(String, index=True, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    role = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    qualifications = Column(Text, nullable=True)
    license_level = Column(String, nullable=True)
    employment_status = Column(String, default="Active")


class Sponsor(Base):
    __tablename__ = "sponsors"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    name = Column(String, index=True, nullable=False)
    industry = Column(String, nullable=True)
    contact_person = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    website = Column(String, nullable=True)
    status = Column(String, default="Prospect")


class FundingOpportunity(Base):
    __tablename__ = "funding_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    title = Column(String, index=True, nullable=True)
    name = Column(String, index=True, nullable=True)
    description = Column(Text, nullable=True)
    amount = Column(Integer, nullable=True)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"), nullable=True)
    deadline = Column(String, nullable=True)
    status = Column(String, default="Open")


class ComplianceTask(Base):
    __tablename__ = "compliance_tasks"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(String, nullable=True)
    status = Column(String, default="Pending")


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=True)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"), nullable=True)
    funding_id = Column(Integer, ForeignKey("funding_opportunities.id"), nullable=True)
    status = Column(String, default="Draft")


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    name = Column(String, index=True, nullable=False)
    location = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)


class Fee(Base):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("fee_categories.id"), nullable=True)
    amount = Column(Integer, nullable=False)
    due_date = Column(String, nullable=True)
    status = Column(String, default="Pending")


class Trial(Base):
    __tablename__ = "trials"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    date = Column(String, nullable=True)
    result = Column(String, nullable=True)
    notes = Column(Text, nullable=True)


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    date = Column(String, nullable=False)
    status = Column(String, nullable=False)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    receiver_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    content = Column(Text, nullable=False)
    timestamp = Column(String, nullable=True)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, default=0)
    status = Column(String, default="Active")


class Camp(Base):
    __tablename__ = "camps"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    name = Column(String, index=True, nullable=False)
    location = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
