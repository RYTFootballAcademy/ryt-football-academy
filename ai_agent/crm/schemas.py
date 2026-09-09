"""Pydantic request/response models for the core CRM API."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ParentCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    whatsapp: Optional[str] = None
    relationship_to_player: Optional[str] = None


class ParentRead(ParentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class PlayerCreate(BaseModel):
    name: str
    age: Optional[int] = Field(default=None, ge=0, le=100)
    position: Optional[str] = None
    parent_id: Optional[int] = None
    team_id: Optional[int] = None
    school: Optional[str] = None
    grade: Optional[str] = None
    status: str = "Active"


class PlayerRead(PlayerCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CoachCreate(BaseModel):
    name: str
    role: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    qualifications: Optional[str] = None
    license_level: Optional[str] = None


class CoachRead(CoachCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employment_status: Optional[str] = None


class SponsorCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    status: str = "Prospect"


class SponsorRead(SponsorCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SponsorStatusUpdate(BaseModel):
    status: str


class FundingCreate(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[int] = None
    sponsor_id: Optional[int] = None
    deadline: Optional[str] = None
    status: str = "Open"


class FundingRead(FundingCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ComplianceCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    status: str = "Pending"


class ComplianceRead(ComplianceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ProposalCreate(BaseModel):
    title: str
    content: Optional[str] = None
    sponsor_id: Optional[int] = None
    funding_id: Optional[int] = None
    status: str = "Draft"


class ProposalRead(ProposalCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TournamentCreate(BaseModel):
    name: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class TournamentRead(TournamentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class FeeCreate(BaseModel):
    player_id: int
    amount: int
    due_date: Optional[str] = None
    status: str = "Pending"
    category_id: Optional[int] = None


class FeeRead(FeeCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TrialCreate(BaseModel):
    player_id: int
    date: Optional[str] = None
    result: Optional[str] = None
    notes: Optional[str] = None


class TrialRead(TrialCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class AttendanceCreate(BaseModel):
    player_id: int
    date: str
    status: str


class AttendanceRead(AttendanceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class MessageCreate(BaseModel):
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None
    content: str
    timestamp: Optional[str] = None


class MessageRead(MessageCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ProductCreate(BaseModel):
    name: str
    price: int = Field(ge=0)
    stock: int = Field(default=0, ge=0)
    category_id: Optional[int] = None
    status: str = "Active"


class ProductRead(ProductCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CampCreate(BaseModel):
    name: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CampRead(CampCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
