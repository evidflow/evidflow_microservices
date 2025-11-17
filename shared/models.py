from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from sqlalchemy import JSON, Text

class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ORG_OWNER = "ORG_OWNER"
    ORG_ADMIN = "ORG_ADMIN"
    MEAL_OFFICER = "MEAL_OFFICER"
    DONOR_VIEW = "DONOR_VIEW"

class OrganizationTier(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"

class ReportType(str, Enum):
    DONOR = "donor"
    INTERNAL = "internal"
    IMPACT_STORY = "impact_story"
    ANALYTICS = "analytics"
    SUMMARY = "summary"

class ReportFormat(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    WORD = "word"
    HTML = "html"

class FeedbackCategory(str, Enum):
    GENERAL = "general"
    SERVICE_DELIVERY = "service_delivery"
    STAFF_BEHAVIOR = "staff_behavior"
    FACILITY = "facility"
    PSEA = "psea"
    FRAUD = "fraud"

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    role: UserRole
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    organization_id: Optional[int] = Field(default=None, foreign_key="organizations.id")
    temp_tier_selection: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    organization: Optional["Organization"] = Relationship(back_populates="users")
    sessions: List["UserSession"] = Relationship(back_populates="user")

class UserSession(SQLModel, table=True):
    __tablename__ = "user_sessions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="sessions")

class Organization(SQLModel, table=True):
    __tablename__ = "organizations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    slug: str = Field(unique=True, index=True)
    description: Optional[str] = None
    tier: OrganizationTier = Field(default=OrganizationTier.STARTER)
    max_users: int = Field(default=50)
    max_beneficiaries: int = Field(default=10000)
    is_active: bool = Field(default=True)
    subscription_status: str = Field(default="active")
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    users: List["User"] = Relationship(back_populates="organization")
    services: List["Service"] = Relationship(back_populates="organization")
    beneficiaries: List["Beneficiary"] = Relationship(back_populates="organization")
    reports: List["Report"] = Relationship(back_populates="organization")
    invitations: List["OrganizationInvitation"] = Relationship(back_populates="organization")

class OrganizationMembership(SQLModel, table=True):
    __tablename__ = "organization_memberships"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    organization_id: int = Field(foreign_key="organizations.id")
    role: str
    is_active: bool = Field(default=True)
    joined_at: datetime = Field(default_factory=datetime.utcnow)

class OrganizationInvitation(SQLModel, table=True):
    __tablename__ = "organization_invitations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    role: str
    invited_by: int = Field(foreign_key="users.id")
    organization_id: int = Field(foreign_key="organizations.id")
    token: str = Field(unique=True, index=True)
    status: InvitationStatus = Field(default=InvitationStatus.PENDING)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    accepted_at: Optional[datetime] = None
    
    organization: Organization = Relationship(back_populates="invitations")

class Beneficiary(SQLModel, table=True):
    __tablename__ = "beneficiaries"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    contact_info: str
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    demographics: Optional[Dict[str, Any]] = Field(default={}, sa_type=JSON)
    vulnerability_score: Optional[float] = Field(default=0.0)
    organization_id: int = Field(foreign_key="organizations.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    organization: Organization = Relationship(back_populates="beneficiaries")
    feedback: List["Feedback"] = Relationship(back_populates="beneficiary")

class Service(SQLModel, table=True):
    __tablename__ = "services"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    category: str
    is_active: bool = Field(default=True)
    organization_id: int = Field(foreign_key="organizations.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    organization: Organization = Relationship(back_populates="services")
    indicators: List["Indicator"] = Relationship(back_populates="service")

class Indicator(SQLModel, table=True):
    __tablename__ = "indicators"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    current_value: float = Field(default=0.0)
    target_value: float = Field(default=0.0)
    unit: str = Field(default="")
    service_id: int = Field(foreign_key="services.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    service: Service = Relationship(back_populates="indicators")

class Feedback(SQLModel, table=True):
    __tablename__ = "feedback"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    beneficiary_id: int = Field(foreign_key="beneficiaries.id")
    rating: int = Field(ge=1, le=5)
    comments: Optional[str] = None
    category: FeedbackCategory = Field(default=FeedbackCategory.GENERAL)
    is_anonymous: bool = Field(default=False)
    organization_id: int = Field(foreign_key="organizations.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    beneficiary: Beneficiary = Relationship(back_populates="feedback")

class Report(SQLModel, table=True):
    __tablename__ = "reports"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    report_type: ReportType
    format: ReportFormat
    file_url: Optional[str] = None
    content: Optional[str] = Field(sa_type=Text)
    organization_id: int = Field(foreign_key="organizations.id")
    generated_by: int = Field(foreign_key="users.id")
    is_public: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    organization: Organization = Relationship(back_populates="reports")

class EmailVerification(SQLModel, table=True):
    __tablename__ = "email_verifications"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    verification_code: str = Field(index=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_at: Optional[datetime] = None

class PasswordReset(SQLModel, table=True):
    __tablename__ = "password_resets"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    reset_code: str = Field(index=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_at: Optional[datetime] = None

class Payment(SQLModel, table=True):
    __tablename__ = "payments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organizations.id")
    stripe_payment_intent_id: str
    amount: int  # in cents
    currency: str = Field(default="usd")
    status: str = Field(default="pending")
    tier: OrganizationTier
    period: str = Field(default="monthly")  # monthly or yearly
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class AnalyticsCache(SQLModel, table=True):
    __tablename__ = "analytics_cache"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organizations.id")
    cache_key: str = Field(index=True)
    data: Dict[str, Any] = Field(default={}, sa_type=JSON)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
