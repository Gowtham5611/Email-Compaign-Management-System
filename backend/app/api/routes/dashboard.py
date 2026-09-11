from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import get_db
from app.database.models.models import (
    User, Campaign, CampaignRecipient, Template, Recipient, RecipientStatus
)
from app.schemas.schemas import DashboardStatsResponse, CampaignResponse
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_campaigns = db.query(Campaign).filter(Campaign.user_id == current_user.id).count()
    total_recipients = db.query(Recipient).filter(Recipient.user_id == current_user.id).count()
    total_templates = db.query(Template).filter(Template.user_id == current_user.id).count()

    # Get campaign IDs for this user
    user_campaign_ids = db.query(Campaign.id).filter(Campaign.user_id == current_user.id).subquery()

    total_emails_sent = db.query(CampaignRecipient).filter(
        CampaignRecipient.campaign_id.in_(user_campaign_ids),
        CampaignRecipient.status == RecipientStatus.SENT
    ).count()

    failed_emails = db.query(CampaignRecipient).filter(
        CampaignRecipient.campaign_id.in_(user_campaign_ids),
        CampaignRecipient.status == RecipientStatus.FAILED
    ).count()

    successful_emails = total_emails_sent

    recent_campaigns = db.query(Campaign).filter(
        Campaign.user_id == current_user.id
    ).order_by(Campaign.id.desc()).limit(5).all()

    return DashboardStatsResponse(
        total_campaigns=total_campaigns,
        total_emails_sent=total_emails_sent,
        successful_emails=successful_emails,
        failed_emails=failed_emails,
        total_recipients=total_recipients,
        total_templates=total_templates,
        recent_campaigns=[CampaignResponse.model_validate(c) for c in recent_campaigns]
    )

