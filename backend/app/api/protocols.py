from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.models.protocol import Protocol
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter()

ALLOWED_STATUSES = ["draft", "pending", "approved", "rejected", "suspended"]


# --- Schemas ---
class ProtocolCreate(BaseModel):
    title: str
    abstract: str

class ProtocolUpdate(BaseModel):
    title: Optional[str] = None
    abstract: Optional[str] = None
    status: Optional[str] = None


# --- Endpoints ---
@router.get("/")
def list_protocols(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Protocol).filter(Protocol.pi_id == current_user.id).all()

@router.get("/{protocol_id}")
def get_protocol(
    protocol_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol олдсонгүй")
    return protocol

@router.post("/", status_code=201)
def create_protocol(
    data: ProtocolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    protocol = Protocol(
        title=data.title,
        abstract=data.abstract,
        pi_id=current_user.id,
        status="draft"
    )
    db.add(protocol)
    db.commit()
    db.refresh(protocol)
    return protocol

@router.patch("/{protocol_id}")
def update_protocol(
    protocol_id: str,
    data: ProtocolUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol олдсонгүй")

    if data.status and data.status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail=f"Зөвшөөрөгдөөгүй статус. Зөвшөөрөгдсөн: {ALLOWED_STATUSES}")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(protocol, field, value)

    db.commit()
    db.refresh(protocol)
    return protocol

@router.delete("/{protocol_id}")
def delete_protocol(
    protocol_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    protocol = db.query(Protocol).filter(Protocol.id == protocol_id).first()
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol олдсонгүй")
    db.delete(protocol)
    db.commit()
    return {"message": "Устгагдлаа"}
