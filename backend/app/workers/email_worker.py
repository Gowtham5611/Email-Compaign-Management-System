import threading
import time
from datetime import datetime
from celery import Celery
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging_config import log_activity
from app.database.database import SessionLocal
from app.database.models.models import (
    Campaign, CampaignRecipient, Template, SMTPSetting,
    CampaignStatus, RecipientStatus
)
from app.services.template_service import TemplateService
from app.services.email_service import EmailService

# Initialize Celery app
celery_app = Celery("email_tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

def process_campaign_execution(campaign_id: int):
    """
    Executes an email campaign asynchronously.
    Updates statuses: QUEUED -> SENDING -> COMPLETED / PARTIALLY_COMPLETED / FAILED / CANCELLED.
    Checks cancellation state after each recipient.
    """
    db: Session = SessionLocal()
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            log_activity(f"ERROR: Worker campaign ID {campaign_id} not found.", level="error")
            return

        if campaign.status == CampaignStatus.CANCELLED:
            log_activity(f"Campaign {campaign_id} was cancelled before worker start.")
            return

        # Set status SENDING
        campaign.status = CampaignStatus.SENDING
        campaign.started_at = datetime.utcnow()
        db.commit()

        # Load Template
        template = db.query(Template).filter(Template.id == campaign.template_id).first()
        if not template:
            campaign.status = CampaignStatus.FAILED
            db.commit()
            log_activity(f"ERROR: Template for campaign {campaign_id} missing.", level="error")
            return

        # Load user SMTP settings if defined
        smtp_user_setting = db.query(SMTPSetting).filter(SMTPSetting.user_id == campaign.user_id).first()
        smtp_config = {}
        if smtp_user_setting:
            smtp_config = {
                "smtp_host": smtp_user_setting.smtp_host,
                "smtp_port": smtp_user_setting.smtp_port,
                "smtp_username": smtp_user_setting.smtp_username,
                "smtp_password": smtp_user_setting.smtp_password,
                "sender_name": smtp_user_setting.sender_name,
            }

        recipients = db.query(CampaignRecipient).filter(
            CampaignRecipient.campaign_id == campaign_id,
            CampaignRecipient.status == RecipientStatus.PENDING
        ).all()

        log_activity(f"Worker starting campaign execution #{campaign_id} '{campaign.name}' for {len(recipients)} recipients.")

        successful = 0
        failed = 0

        for cr in recipients:
            # Re-fetch campaign status to detect real-time cancellation signal
            db.refresh(campaign)
            if campaign.status == CampaignStatus.CANCELLED:
                log_activity(f"Campaign #{campaign_id} execution halted due to user cancellation.")
                break

            # Mark recipient sending
            cr.status = RecipientStatus.SENDING
            db.commit()

            # Prepare data dictionary for dynamic placeholder interpolation
            merge_data = {
                "name": cr.recipient_name,
                "email": cr.recipient_email,
                "subject": template.subject,
                **(cr.custom_fields or {})
            }

            # Render template subject & body safely
            rendered_subject = TemplateService.render_template(template.subject, merge_data)
            rendered_body = TemplateService.render_template(template.body, merge_data)

            # Send Email
            success, error_msg, retries_used = EmailService.send_single_email(
                recipient_email=cr.recipient_email,
                subject=rendered_subject,
                plain_text_body=rendered_body,
                attachment_path=campaign.attachment_path,
                smtp_config=smtp_config,
                max_retries=settings.MAX_RETRIES
            )

            cr.retry_count = retries_used
            if success:
                cr.status = RecipientStatus.SENT
                cr.sent_at = datetime.utcnow()
                cr.error_message = None
                successful += 1
            else:
                cr.status = RecipientStatus.FAILED
                cr.error_message = error_msg
                failed += 1

            db.commit()
            time.sleep(0.5) # Prevent aggressive SMTP throttling

        # Update final campaign status
        db.refresh(campaign)
        if campaign.status != CampaignStatus.CANCELLED:
            campaign.successful_count = db.query(CampaignRecipient).filter(
                CampaignRecipient.campaign_id == campaign_id,
                CampaignRecipient.status == RecipientStatus.SENT
            ).count()
            campaign.failed_count = db.query(CampaignRecipient).filter(
                CampaignRecipient.campaign_id == campaign_id,
                CampaignRecipient.status == RecipientStatus.FAILED
            ).count()
            campaign.completed_at = datetime.utcnow()

            if campaign.failed_count == 0:
                campaign.status = CampaignStatus.COMPLETED
            elif campaign.successful_count > 0:
                campaign.status = CampaignStatus.PARTIALLY_COMPLETED
            else:
                campaign.status = CampaignStatus.FAILED

            db.commit()
            log_activity(f"Campaign #{campaign_id} completed: {campaign.successful_count} sent, {campaign.failed_count} failed.")

    except Exception as e:
        log_activity(f"Unhandled exception in worker executing campaign {campaign_id}: {str(e)}", level="error")
    finally:
        db.close()

@celery_app.task(name="tasks.execute_campaign")
def celery_execute_campaign(campaign_id: int):
    process_campaign_execution(campaign_id)

def dispatch_campaign_task(campaign_id: int):
    """
    Attempts to dispatch task to Celery queue, with fallback to background thread
    if Redis / Celery worker is unavailable.
    """
    try:
        celery_execute_campaign.delay(campaign_id)
        log_activity(f"Dispatched campaign #{campaign_id} to Celery queue.")
    except Exception as err:
        log_activity(f"Celery queue unavailable ({err}). Falling back to threaded background worker for campaign #{campaign_id}.")
        t = threading.Thread(target=process_campaign_execution, args=(campaign_id,), daemon=True)
        t.start()

