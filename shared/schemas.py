from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models import UserRole, OrganizationTier, ReportType, ReportFormat, FeedbackCategory

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.MEAL_OFFICER

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    organization_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrganizationCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    tier: OrganizationTier

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tier: Optional[OrganizationTier] = None

class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    tier: OrganizationTier
    max_users: int
    max_beneficiaries: int
    is_active: bool
    subscription_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class BeneficiaryCreate(BaseModel):
    name: str
    contact_info: str
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    demographics: Optional[Dict[str, Any]] = None
    organization_id: int

class BeneficiaryUpdate(BaseModel):
    name: Optional[str] = None
    contact_info: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    demographics: Optional[Dict[str, Any]] = None

class BeneficiaryResponse(BaseModel):
    id: int
    name: str
    contact_info: str
    age: Optional[int]
    gender: Optional[str]
    location: Optional[str]
    demographics: Dict[str, Any]
    organization_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    organization_id: int

class ServiceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: str
    is_active: bool
    organization_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class IndicatorCreate(BaseModel):
    name: str
    description: Optional[str] = None
    current_value: float
    target_value: float
    unit: str
    service_id: int

class IndicatorResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    current_value: float
    target_value: float
    unit: str
    service_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class FeedbackCreate(BaseModel):
    beneficiary_id: int
    rating: int
    comments: Optional[str] = None
    category: FeedbackCategory = FeedbackCategory.GENERAL
    is_anonymous: bool = False

class FeedbackResponse(BaseModel):
    id: int
    beneficiary_id: int
    rating: int
    comments: Optional[str]
    category: FeedbackCategory
    is_anonymous: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReportCreate(BaseModel):
    title: str
    report_type: ReportType
    format: ReportFormat = ReportFormat.PDF
    organization_id: int
    generated_by: int

class ReportResponse(BaseModel):
    id: int
    title: str
    report_type: ReportType
    format: ReportFormat
    file_url: Optional[str]
    organization_id: int
    generated_by: int
    is_public: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class DashboardResponse(BaseModel):
    services_count: int
    indicators_count: int
    beneficiaries_count: int
    feedback_count: int
    average_rating: float
    indicator_performance: List[Dict[str, Any]]
    recent_activities: List[Dict[str, Any]]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TierSelection(BaseModel):
    tier: OrganizationTier

class PaymentCreate(BaseModel):
    tier: OrganizationTier
    period: str = "monthly"  # monthly or yearly
    success_url: str
    cancel_url: str

class PaymentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: int
    currency: str

class AIInsightsRequest(BaseModel):
    data: Dict[str, Any]
    context: str
    analysis_type: str

class AIInsightsResponse(BaseModel):
    insights: Dict[str, Any]
    generated_at: datetime
    model: str

class DataImportRequest(BaseModel):
    file_type: str  # csv, excel, json
    organization_id: int
    mapping: Dict[str, str]

class DataImportResponse(BaseModel):
    imported_count: int
    errors: List[str]
    total_rows: int
    import_id: str
