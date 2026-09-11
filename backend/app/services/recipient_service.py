from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.database.models.models import Recipient, RecipientGroup, recipient_group_members
from app.schemas.schemas import RecipientCreate, RecipientGroupCreate

class RecipientService:
    @staticmethod
    def get_recipients(
        db: Session, user_id: int, skip: int = 0, limit: int = 100, search: Optional[str] = None
    ) -> Tuple[List[Recipient], int]:
        query = db.query(Recipient).filter(Recipient.user_id == user_id)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Recipient.name.ilike(search_pattern)) | (Recipient.email.ilike(search_pattern))
            )
        total = query.count()
        items = query.order_by(Recipient.id.desc()).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def create_recipient(db: Session, user_id: int, recipient_in: RecipientCreate) -> Recipient:
        recipient = Recipient(
            user_id=user_id,
            name=recipient_in.name,
            email=recipient_in.email.lower(),
            custom_fields=recipient_in.custom_fields
        )
        db.add(recipient)
        db.commit()
        db.refresh(recipient)
        return recipient

    @staticmethod
    def bulk_import_recipients(
        db: Session, user_id: int, valid_rows: List[Dict[str, Any]], group_name: Optional[str] = None
    ) -> Tuple[int, Optional[RecipientGroup]]:
        created_count = 0
        group = None

        if group_name:
            group = RecipientGroup(user_id=user_id, name=group_name)
            db.add(group)
            db.commit()
            db.refresh(group)

        for row in valid_rows:
            email = row["email"].lower()
            existing = db.query(Recipient).filter(
                Recipient.user_id == user_id, Recipient.email == email
            ).first()

            if not existing:
                existing = Recipient(
                    user_id=user_id,
                    name=row.get("name", "Recipient"),
                    email=email,
                    custom_fields=row.get("custom_fields", {})
                )
                db.add(existing)
                db.commit()
                db.refresh(existing)
                created_count += 1
            else:
                if row.get("custom_fields"):
                    existing.custom_fields = {**(existing.custom_fields or {}), **row.get("custom_fields")}
                    db.commit()

            if group and existing not in group.recipients:
                group.recipients.append(existing)
                db.commit()

        return created_count, group

