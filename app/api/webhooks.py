# app/api/webhooks.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models import Webhook
from app.db.database import SessionLocal
from app.services.webhook_service import test_webhook
from pydantic import BaseModel

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

# ----------------------------
# DB Session
# ----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------
# Pydantic Schemas
# ----------------------------
class WebhookCreate(BaseModel):
    url: str
    event: str
    enabled: bool = True

class WebhookResponse(WebhookCreate):
    id: int

# ----------------------------
# LIST ALL WEBHOOKS
# ----------------------------
@router.get("/", response_model=list[WebhookResponse])
def list_webhooks(db: Session = Depends(get_db)):
    webhooks = db.query(Webhook).all()
    # map DB column `event_type` to API field `event`
    return [
        WebhookResponse(
            id=w.id,
            url=w.url,
            event=w.event_type,
            enabled=w.enabled
        )
        for w in webhooks
    ]

# ----------------------------
# ADD A NEW WEBHOOK
# ----------------------------
@router.post("/", response_model=WebhookResponse)
def add_webhook(data: WebhookCreate, db: Session = Depends(get_db)):
    webhook = Webhook(
        url=data.url,
        event_type=data.event,  # map API field to DB column
        enabled=data.enabled
    )
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    return WebhookResponse(
        id=webhook.id,
        url=webhook.url,
        event=webhook.event_type,  # map back for response
        enabled=webhook.enabled
    )

# ----------------------------
# TEST WEBHOOK
# ----------------------------
@router.post("/test/{id}")
def test(id: int, db: Session = Depends(get_db)):
    webhook = db.query(Webhook).filter(Webhook.id == id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    try:
        result = test_webhook(webhook.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook test failed: {str(e)}")
    return {"webhook_id": id, "test_result": result}

# ----------------------------
# DELETE WEBHOOK
# ----------------------------
@router.delete("/{id}")
def delete(id: int, db: Session = Depends(get_db)):
    webhook = db.query(Webhook).filter(Webhook.id == id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    db.delete(webhook)
    db.commit()
    return {"message": "Webhook deleted"}
