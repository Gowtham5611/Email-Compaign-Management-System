import os
import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models.models import User, Campaign, CampaignRecipient, CampaignStatus
from app.schemas.schemas import (
    CampaignCreate, CampaignResponse, CampaignProgressResponse, CampaignRecipientResponse
)
from app.api.dependencies import get_current_user
from app.services.campaign_service import CampaignService
from app.workers.email_worker import dispatch_campaign_task
from app.core.config import settings

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

@router.get("", response_model=List[CampaignResponse])
def list_campaigns(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Campaign).filter(Campaign.user_id == current_user.id).order_by(Campaign.id.desc()).all()

@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    name: str = Form(...),
    template_id: int = Form(...),
    recipient_ids: Optional[str] = Form(None), # JSON list or comma-separated
    recipient_group_ids: Optional[str] = Form(None),
    raw_recipients: Optional[str] = Form(None), # JSON string of CSV rows
    attachment: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    parsed_recipient_ids = json.loads(recipient_ids) if recipient_ids else None
    parsed_group_ids = json.loads(recipient_group_ids) if recipient_group_ids else None
    parsed_raw = json.loads(raw_recipients) if raw_recipients else None

    attachment_filename = None
    attachment_path = None

    if attachment and attachment.filename:
        # File size check
        content = await attachment.read()
        if len(content) > settings.ATTACHMENT_MAX_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"Attachment size exceeds max limit of {settings.ATTACHMENT_MAX_SIZE_MB}MB"
            )

        unique_name = f"{uuid.uuid4().hex}_{os.path.basename(attachment.filename)}"
        attachment_path = os.path.join(settings.UPLOAD_DIR, unique_name)
        attachment_filename = attachment.filename

        with open(attachment_path, "wb") as f:
            f.write(content)

    campaign_in = CampaignCreate(
        name=name,
        template_id=template_id,
        recipient_ids=parsed_recipient_ids,
        recipient_group_ids=parsed_group_ids,
        raw_recipients=parsed_raw
    )

    try:
        campaign = CampaignService.create_campaign(
            db, current_user.id, campaign_in, attachment_filename, attachment_path
        )
        return campaign
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=CampaignResponse)
def get_campaign(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == id, Campaign.user_id == current_user.id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.post("/{id}/send", response_model=CampaignResponse)
def send_campaign(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == id, Campaign.user_id == current_user.id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.status in (CampaignStatus.SENDING, CampaignStatus.QUEUED):
        raise HTTPException(status_code=400, detail="Campaign is already queued or currently sending.")

    if campaign.total_recipients == 0:
        raise HTTPException(status_code=400, detail="Campaign has no valid recipients.")

    campaign.status = CampaignStatus.QUEUED
    db.commit()
    db.refresh(campaign)

    # Trigger background worker asynchronously without blocking HTTP response
    dispatch_campaign_task(campaign.id)

    return campaign

@router.post("/{id}/cancel", response_model=CampaignResponse)
def cancel_campaign(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == id, Campaign.user_id == current_user.id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign = CampaignService.cancel_campaign(db, campaign)
    return campaign

@router.get("/{id}/progress", response_model=CampaignProgressResponse)
def get_campaign_progress(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == id, Campaign.user_id == current_user.id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return CampaignService.get_progress(db, campaign)

@router.get("/{id}/recipients", response_model=List[CampaignRecipientResponse])
def get_campaign_recipients(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == id, Campaign.user_id == current_user.id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    recipients = db.query(CampaignRecipient).filter(CampaignRecipient.campaign_id == campaign.id).all()
    return recipients

