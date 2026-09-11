from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models.models import (
    Campaign, CampaignRecipient, Template, Recipient, RecipientGroup,
    CampaignStatus, RecipientStatus
)
from app.schemas.schemas import CampaignCreate, CampaignProgressResponse, CampaignRecipientResponse

class CampaignService:
    @staticmethod
    def create_campaign(
        db: Session,
        user_id: int,
        campaign_in: CampaignCreate,
        attachment_filename: Optional[str] = None,
        attachment_path: Optional[str] = None
    ) -> Campaign:
        # Check template existence
        template = db.query(Template).filter(
            Template.id == campaign_in.template_id, Template.user_id == user_id
        ).first()

        if not template:
            raise ValueError(f"Template ID {campaign_in.template_id} not found.")

        recipients_map = {} # email -> {name, custom_fields, recipient_id}

        # 1. From recipient IDs
        if campaign_in.recipient_ids:
            recs = db.query(Recipient).filter(
                Recipient.id.in_(campaign_in.recipient_ids), Recipient.user_id == user_id
            ).all()
            for r in recs:
                recipients_map[r.email.lower()] = {
                    "recipient_id": r.id,
                    "name": r.name,
                    "email": r.email.lower(),
                    "custom_fields": r.custom_fields
                }

        # 2. From recipient groups
        if campaign_in.recipient_group_ids:
            groups = db.query(RecipientGroup).filter(
                RecipientGroup.id.in_(campaign_in.recipient_group_ids), RecipientGroup.user_id == user_id
            ).all()
            for g in groups:
                for r in g.recipients:
                    recipients_map[r.email.lower()] = {
                        "recipient_id": r.id,
                        "name": r.name,
                        "email": r.email.lower(),
                        "custom_fields": r.custom_fields
                    }

        # 3. From raw CSV upload rows
        if campaign_in.raw_recipients:
            for row in campaign_in.raw_recipients:
                email = row.get("email", "").lower()
                if email and email not in recipients_map:
                    recipients_map[email] = {
                        "recipient_id": None,
                        "name": row.get("name", "Recipient"),
                        "email": email,
                        "custom_fields": row.get("custom_fields", {})
                    }

        campaign = Campaign(
            user_id=user_id,
            name=campaign_in.name,
            template_id=campaign_in.template_id,
            status=CampaignStatus.DRAFT,
            total_recipients=len(recipients_map),
            attachment_filename=attachment_filename,
            attachment_path=attachment_path
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        # Create CampaignRecipient records
        for email, rdata in recipients_map.items():
            cr = CampaignRecipient(
                campaign_id=campaign.id,
                recipient_id=rdata["recipient_id"],
                recipient_email=email,
                recipient_name=rdata["name"],
                custom_fields=rdata["custom_fields"],
                status=RecipientStatus.PENDING
            )
            db.add(cr)
        
        db.commit()
        db.refresh(campaign)
        return campaign

    @staticmethod
    def get_progress(db: Session, campaign: Campaign) -> CampaignProgressResponse:
        recipients = db.query(CampaignRecipient).filter(
            CampaignRecipient.campaign_id == campaign.id
        ).all()

        total = len(recipients)
        sent = sum(1 for r in recipients if r.status == RecipientStatus.SENT)
        failed = sum(1 for r in recipients if r.status == RecipientStatus.FAILED)
        cancelled = sum(1 for r in recipients if r.status == RecipientStatus.CANCELLED)
        pending = sum(1 for r in recipients if r.status in (RecipientStatus.PENDING, RecipientStatus.SENDING))

        processed = sent + failed + cancelled
        percentage = round((processed / total * 100), 1) if total > 0 else 0.0

        recipient_summaries = [
            CampaignRecipientResponse.model_validate(r) for r in recipients
        ]

        return CampaignProgressResponse(
            campaign_id=campaign.id,
            status=campaign.status,
            total=total,
            sent=sent,
            failed=failed,
            pending=pending,
            cancelled=cancelled,
            percentage=percentage,
            recipients_summary=recipient_summaries
        )

    @staticmethod
    def cancel_campaign(db: Session, campaign: Campaign) -> Campaign:
        """
        Preserves Stop/Cancel functionality:
        Stops processing pending recipients, marks pending as CANCELLED, and updates campaign status.
        Does not interrupt an email currently being sent.
        """
        pending_recipients = db.query(CampaignRecipient).filter(
            CampaignRecipient.campaign_id == campaign.id,
            CampaignRecipient.status.in_([RecipientStatus.PENDING, RecipientStatus.SENDING])
        ).all()

        for cr in pending_recipients:
            cr.status = RecipientStatus.CANCELLED
            cr.error_message = "Campaign cancelled by user"

        campaign.status = CampaignStatus.CANCELLED
        campaign.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(campaign)
        return campaign

