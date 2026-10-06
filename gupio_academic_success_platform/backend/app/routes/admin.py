import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.dependencies import require_roles
from app.models import AuditEvent, User

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/audit")
def audit_log(user: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    rows = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(100).all()
    return {
        "events": [
            {
                "id": r.id,
                "actor_user_id": r.actor_user_id,
                "action": r.action,
                "ip_address": r.ip_address,
                "metadata": json.loads(r.metadata_json) if r.metadata_json else None,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
    }
