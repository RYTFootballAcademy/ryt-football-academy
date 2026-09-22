"""Extended FAOS data model.

This module implements the additional tables described in
``DATABASE_SPECIFICATION.md``. Core CRM tables live in ``ai_agent.crm.models``
for backwards compatibility; everything shares the same SQLAlchemy ``Base`` and
the same database connection.
"""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text

from ai_agent.modules.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    registration_number = Column(String, nullable=True)
    npo_number = Column(String, nullable=True)
    established = Column(String, nullable=True)
    town = Column(String, nullable=True)
    province = Column(String, nullable=True)
    country = Column(String, default="South Africa")
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    website = Column(String, nullable=True)
    status = Column(String, default="Active")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    name = Column(String, nullable=False)
    age_group = Column(String, nullable=True)
    season = Column(String, nullable=True)
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=True)
    training_days = Column(String, nullable=True)
    training_time = Column(String, nullable=True)
    venue = Column(String, nullable=True)


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=True)
    date = Column(String, nullable=False)
    time = Column(String, nullable=True)
    venue = Column(String, nullable=True)
    focus_area = Column(String, nullable=True)
    notes = Column(Text, nullable=True)


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    opponent = Column(String, nullable=False)
    date = Column(String, nullable=False)
    venue = Column(String, nullable=True)
    competition = Column(String, nullable=True)
    result = Column(String, nullable=True)


class MatchEvent(Base):
    __tablename__ = "match_events"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    event_type = Column(String, nullable=False)
    minute = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)


class PlayerStatistic(Base):
    __tablename__ = "player_statistics"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    season = Column(String, nullable=True)
    matches_played = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    minutes_played = Column(Integer, default=0)


class DevelopmentReport(Base):
    __tablename__ = "development_reports"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=True)
    date = Column(String, nullable=False)
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)


class Injury(Base):
    __tablename__ = "injuries"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    injury_type = Column(String, nullable=False)
    date = Column(String, nullable=False)
    recovery_date = Column(String, nullable=True)
    status = Column(String, default="Active")


class FitnessTest(Base):
    __tablename__ = "fitness_tests"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    date = Column(String, nullable=False)
    test_type = Column(String, nullable=False)
    result = Column(String, nullable=True)
    notes = Column(Text, nullable=True)


class FeeCategory(Base):
    __tablename__ = "fee_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)


class PlayerPayment(Base):
    __tablename__ = "player_payments"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    fee_id = Column(Integer, ForeignKey("fees.id"), nullable=True)
    amount = Column(Integer, nullable=False)
    date = Column(String, nullable=False)
    method = Column(String, nullable=True)
    reference = Column(String, nullable=True)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    description = Column(Text, nullable=False)
    amount = Column(Integer, nullable=False)
    date = Column(String, nullable=False)
    category = Column(String, nullable=True)


class Income(Base):
    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    source = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    date = Column(String, nullable=False)


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    year = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    bank_name = Column(String, nullable=False)
    account_number = Column(String, nullable=True)
    account_type = Column(String, nullable=True)
    status = Column(String, default="Active")


class SponsorContact(Base):
    __tablename__ = "sponsor_contacts"

    id = Column(Integer, primary_key=True, index=True)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"), nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)


class SponsorshipPackage(Base):
    __tablename__ = "sponsorship_packages"

    id = Column(Integer, primary_key=True, index=True)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    value = Column(Integer, nullable=True)


class SponsorshipAgreement(Base):
    __tablename__ = "sponsorship_agreements"

    id = Column(Integer, primary_key=True, index=True)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"), nullable=False)
    package_id = Column(Integer, ForeignKey("sponsorship_packages.id"), nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    status = Column(String, default="Active")


class SponsorMeeting(Base):
    __tablename__ = "sponsor_meetings"

    id = Column(Integer, primary_key=True, index=True)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"), nullable=False)
    date = Column(String, nullable=False)
    notes = Column(Text, nullable=True)


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    date = Column(String, nullable=False)
    notes = Column(Text, nullable=True)


class GrantApplication(Base):
    __tablename__ = "grant_applications"

    id = Column(Integer, primary_key=True, index=True)
    funding_id = Column(Integer, ForeignKey("funding_opportunities.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    date = Column(String, nullable=False)
    status = Column(String, default="Submitted")
    notes = Column(Text, nullable=True)


class SupportingDocument(Base):
    __tablename__ = "supporting_documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("grant_applications.id"), nullable=False)
    file_path = Column(String, nullable=False)
    description = Column(Text, nullable=True)


class FundingOutcome(Base):
    __tablename__ = "funding_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("grant_applications.id"), nullable=False)
    decision = Column(String, nullable=False)
    date = Column(String, nullable=True)
    notes = Column(Text, nullable=True)


class Director(Base):
    __tablename__ = "directors"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    role = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    status = Column(String, default="Active")


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    membership_type = Column(String, nullable=True)


class GovernanceMeeting(Base):
    __tablename__ = "governance_meetings"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    date = Column(String, nullable=False)
    type = Column(String, nullable=True)
    notes = Column(Text, nullable=True)


class Resolution(Base):
    __tablename__ = "resolutions"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("governance_meetings.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    status = Column(String, nullable=True)


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    version = Column(String, nullable=True)
    status = Column(String, default="Active")


class AnnualReturn(Base):
    __tablename__ = "annual_returns"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    year = Column(Integer, nullable=False)
    date_filed = Column(String, nullable=True)
    status = Column(String, default="Pending")


class ConstitutionVersion(Base):
    __tablename__ = "constitution_versions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    version = Column(String, nullable=False)
    date = Column(String, nullable=True)
    content = Column(Text, nullable=True)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    date = Column(String, nullable=False)
    status = Column(String, default="Pending")
    total = Column(Integer, default=0)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Integer, nullable=False)


class OrderPayment(Base):
    __tablename__ = "order_payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    date = Column(String, nullable=False)
    method = Column(String, nullable=True)
    reference = Column(String, nullable=True)


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    camp_id = Column(Integer, ForeignKey("camps.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    date = Column(String, nullable=False)
    status = Column(String, default="Pending")


class CampPayment(Base):
    __tablename__ = "camp_payments"

    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("registrations.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    date = Column(String, nullable=False)
    method = Column(String, nullable=True)


class CampAttendance(Base):
    __tablename__ = "camp_attendance"

    id = Column(Integer, primary_key=True, index=True)
    camp_id = Column(Integer, ForeignKey("camps.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    date = Column(String, nullable=False)
    status = Column(String, nullable=False)


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"), nullable=True)
    conversation_date = Column(String, nullable=False)
    input_text = Column(Text, nullable=False)
    output_text = Column(Text, nullable=True)
    context = Column(Text, nullable=True)
    status = Column(String, default="Completed")


class GeneratedProposal(Base):
    __tablename__ = "generated_proposals"

    id = Column(Integer, primary_key=True, index=True)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"), nullable=True)
    proposal_date = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    generated_by = Column(String, default="FAOS")
    status = Column(String, default="Draft")


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    report_date = Column(String, nullable=False)
    report_type = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    generated_by = Column(String, default="FAOS")
    status = Column(String, default="Draft")


class SponsorRecommendation(Base):
    __tablename__ = "sponsor_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"), nullable=False)
    recommendation_date = Column(String, nullable=False)
    recommendation_type = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    status = Column(String, default="Open")


class FundingRecommendation(Base):
    __tablename__ = "funding_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    funding_opportunity_id = Column(Integer, ForeignKey("funding_opportunities.id"), nullable=False)
    recommendation_date = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    status = Column(String, default="Open")


class PlayerInsight(Base):
    __tablename__ = "player_insights"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    insight_date = Column(String, nullable=False)
    insight_type = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    status = Column(String, default="Open")
