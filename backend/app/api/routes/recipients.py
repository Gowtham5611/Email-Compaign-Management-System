from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models.models import User, Recipient, RecipientGroup
from app.schemas.schemas import (
    RecipientCreate, RecipientResponse, CSVValidationResult,
    RecipientGroupCreate, RecipientGroupResponse
)
from app.api.dependencies import get_current_user
from app.services.csv_service import CSVService
from app.services.recipient_service import RecipientService

router = APIRouter(prefix="/recipients", tags=["Recipients"])

@router.post("/upload", response_model=CSVValidationResult)
async def upload_and_validate_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported.")

    content = await file.read()
    result = CSVService.parse_and_validate_csv(content)
    return result

@router.post("/import", response_model=dict)
def import_valid_recipients(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    valid_rows = data.get("valid_rows", [])
    group_name = data.get("group_name")
    
    if not valid_rows:
        raise HTTPException(status_code=400, detail="No valid rows provided for import.")

    count, group = RecipientService.bulk_import_recipients(
        db, current_user.id, valid_rows, group_name
    )
    return {
        "message": f"Successfully imported {count} recipients.",
        "imported_count": count,
        "group_id": group.id if group else None
    }

@router.get("", response_model=dict)
def list_recipients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items, total = RecipientService.get_recipients(
        db, current_user.id, skip=skip, limit=limit, search=search
    )
    return {
        "total": total,
        "items": [RecipientResponse.model_validate(r) for r in items]
    }

@router.post("", response_model=RecipientResponse, status_code=status.HTTP_201_CREATED)
def create_recipient(
    recipient_in: RecipientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Recipient).filter(
        Recipient.user_id == current_user.id,
        Recipient.email == recipient_in.email.lower()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Recipient with this email already exists.")

    return RecipientService.create_recipient(db, current_user.id, recipient_in)

@router.get("/{id}", response_model=RecipientResponse)
def get_recipient(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    recipient = db.query(Recipient).filter(Recipient.id == id, Recipient.user_id == current_user.id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return recipient

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipient(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    recipient = db.query(Recipient).filter(Recipient.id == id, Recipient.user_id == current_user.id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    db.delete(recipient)
    db.commit()
    return None

@router.get("/groups/list", response_model=List[RecipientGroupResponse])
def list_groups(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    groups = db.query(RecipientGroup).filter(RecipientGroup.user_id == current_user.id).all()
    res = []
    for g in groups:
        res.append({
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "recipient_count": len(g.recipients),
            "created_at": g.created_at
        })
    return res

