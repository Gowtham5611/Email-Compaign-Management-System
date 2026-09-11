from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models.models import User, SMTPSetting
from app.schemas.schemas import SMTPSettingCreate, SMTPSettingResponse
from app.api.dependencies import get_current_user
from app.services.email_service import EmailService

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("", response_model=SMTPSettingResponse)
def get_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    setting = db.query(SMTPSetting).filter(SMTPSetting.user_id == current_user.id).first()
    if not setting:
        # Return default from env
        return {
            "id": 0,
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 465,
            "smtp_username": "",
            "sender_name": "Email Campaign Management System",
            "use_tls": True,
            "is_password_set": False,
            "created_at": current_user.created_at,
            "updated_at": current_user.created_at
        }
    
    return {
        "id": setting.id,
        "smtp_host": setting.smtp_host,
        "smtp_port": setting.smtp_port,
        "smtp_username": setting.smtp_username or "",
        "sender_name": setting.sender_name or "Email Campaign Management System",
        "use_tls": bool(setting.use_tls),
        "is_password_set": bool(setting.smtp_password),
        "created_at": setting.created_at,
        "updated_at": setting.updated_at
    }

@router.post("", response_model=SMTPSettingResponse)
def save_settings(
    setting_in: SMTPSettingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    setting = db.query(SMTPSetting).filter(SMTPSetting.user_id == current_user.id).first()

    if not setting:
        setting = SMTPSetting(
            user_id=current_user.id,
            smtp_host=setting_in.smtp_host,
            smtp_port=setting_in.smtp_port,
            smtp_username=setting_in.smtp_username,
            sender_name=setting_in.sender_name,
            use_tls=1 if setting_in.use_tls else 0
        )
        if setting_in.smtp_password:
            setting.smtp_password = setting_in.smtp_password
        db.add(setting)
    else:
        setting.smtp_host = setting_in.smtp_host
        setting.smtp_port = setting_in.smtp_port
        setting.smtp_username = setting_in.smtp_username
        setting.sender_name = setting_in.sender_name
        setting.use_tls = 1 if setting_in.use_tls else 0
        
        # Only update password if provided
        if setting_in.smtp_password and setting_in.smtp_password.strip():
            setting.smtp_password = setting_in.smtp_password

    db.commit()
    db.refresh(setting)

    return {
        "id": setting.id,
        "smtp_host": setting.smtp_host,
        "smtp_port": setting.smtp_port,
        "smtp_username": setting.smtp_username or "",
        "sender_name": setting.sender_name or "Email Campaign Management System",
        "use_tls": bool(setting.use_tls),
        "is_password_set": bool(setting.smtp_password),
        "created_at": setting.created_at,
        "updated_at": setting.updated_at
    }

@router.post("/test-smtp")
def test_smtp_connection(
    setting_in: SMTPSettingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    password = setting_in.smtp_password
    if not password:
        # Check if saved in DB
        setting = db.query(SMTPSetting).filter(SMTPSetting.user_id == current_user.id).first()
        if setting and setting.smtp_password:
            password = setting.smtp_password

    smtp_cfg = {
        "smtp_host": setting_in.smtp_host,
        "smtp_port": setting_in.smtp_port,
        "smtp_username": setting_in.smtp_username,
        "smtp_password": password
    }

    success, message = EmailService.test_smtp_connection(smtp_cfg)
    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"message": message}

