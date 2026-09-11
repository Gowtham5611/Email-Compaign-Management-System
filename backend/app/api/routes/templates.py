from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models.models import User, Template
from app.schemas.schemas import (
    TemplateCreate, TemplateUpdate, TemplateResponse,
    TemplatePreviewRequest, TemplatePreviewResponse
)
from app.api.dependencies import get_current_user
from app.services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["Templates"])

@router.get("", response_model=List[TemplateResponse])
def list_templates(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Template).filter(Template.user_id == current_user.id).order_by(Template.id.desc()).all()

@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    template_in: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    template = Template(
        user_id=current_user.id,
        name=template_in.name,
        subject=template_in.subject,
        body=template_in.body,
        description=template_in.description
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.get("/{id}", response_model=TemplateResponse)
def get_template(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    template = db.query(Template).filter(Template.id == id, Template.user_id == current_user.id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/{id}", response_model=TemplateResponse)
def update_template(
    id: int,
    template_in: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    template = db.query(Template).filter(Template.id == id, Template.user_id == current_user.id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    if template_in.name is not None:
        template.name = template_in.name
    if template_in.subject is not None:
        template.subject = template_in.subject
    if template_in.body is not None:
        template.body = template_in.body
    if template_in.description is not None:
        template.description = template_in.description

    db.commit()
    db.refresh(template)
    return template

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    template = db.query(Template).filter(Template.id == id, Template.user_id == current_user.id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(template)
    db.commit()
    return None

@router.post("/{id}/duplicate", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
def duplicate_template(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    original = db.query(Template).filter(Template.id == id, Template.user_id == current_user.id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Template not found")

    duplicated = Template(
        user_id=current_user.id,
        name=f"{original.name} (Copy)",
        subject=original.subject,
        body=original.body,
        description=original.description
    )
    db.add(duplicated)
    db.commit()
    db.refresh(duplicated)
    return duplicated

@router.post("/preview", response_model=TemplatePreviewResponse)
def preview_template(req: TemplatePreviewRequest):
    rendered_subject, rendered_body, detected_vars = TemplateService.preview(
        req.subject, req.body, req.sample_data
    )
    return {
        "rendered_subject": rendered_subject,
        "rendered_body": rendered_body,
        "detected_variables": detected_vars
    }

