from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.database.models.models import CampaignStatus, RecipientStatus

# ================= AUTH SCHEMAS =================
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ================= SMTP SCHEMAS =================
class SMTPSettingBase(BaseModel):
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465
    smtp_username: Optional[str] = None
    sender_name: str = "Email Campaign Management System"
    use_tls: bool = True

class SMTPSettingCreate(SMTPSettingBase):
    smtp_password: Optional[str] = None

class SMTPSettingResponse(SMTPSettingBase):
    id: int
    is_password_set: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ================= TEMPLATE SCHEMAS =================
class TemplateBase(BaseModel):
    name: str
    subject: str
    body: str
    description: Optional[str] = None

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    description: Optional[str] = None

class TemplateResponse(TemplateBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TemplatePreviewRequest(BaseModel):
    subject: str
    body: str
    sample_data: Dict[str, Any] = Field(default_factory=lambda: {"name": "John Doe", "email": "john@example.com", "subject": "Quarterly Update"})

class TemplatePreviewResponse(BaseModel):
    rendered_subject: str
    rendered_body: str
    detected_variables: List[str]

# ================= RECIPIENT SCHEMAS =================
class RecipientBase(BaseModel):
    name: str
    email: EmailStr
    custom_fields: Optional[Dict[str, Any]] = None

class RecipientCreate(RecipientBase):
    pass

class RecipientResponse(RecipientBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RecipientGroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    recipient_ids: Optional[List[int]] = []

class RecipientGroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    recipient_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CSVRowError(BaseModel):
    row: int
    raw_data: Dict[str, Any]
    reason: str

class CSVValidationResult(BaseModel):
    total_rows: int
    valid_count: int
    invalid_count: int
    duplicate_count: int
    valid_rows: List[Dict[str, Any]]
    invalid_rows: List[CSVRowError]
    detected_columns: List[str]

# ================= CAMPAIGN SCHEMAS =================
class CampaignCreate(BaseModel):
    name: str
    template_id: int
    recipient_ids: Optional[List[int]] = None
    recipient_group_ids: Optional[List[int]] = None
    raw_recipients: Optional[List[Dict[str, Any]]] = None

class CampaignRecipientResponse(BaseModel):
    id: int
    recipient_email: str
    recipient_name: str
    status: RecipientStatus
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    retry_count: int

    model_config = ConfigDict(from_attributes=True)

class CampaignResponse(BaseModel):
    id: int
    name: str
    template_id: Optional[int] = None
    status: CampaignStatus
    total_recipients: int
    successful_count: int
    failed_count: int
    attachment_filename: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class CampaignProgressResponse(BaseModel):
    campaign_id: int
    status: CampaignStatus
    total: int
    sent: int
    failed: int
    pending: int
    cancelled: int
    percentage: float
    recipients_summary: List[CampaignRecipientResponse] = []

# ================= DASHBOARD SCHEMAS =================
class DashboardStatsResponse(BaseModel):
    total_campaigns: int
    total_emails_sent: int
    successful_emails: int
    failed_emails: int
    total_recipients: int
    total_templates: int
    recent_campaigns: List[CampaignResponse]

