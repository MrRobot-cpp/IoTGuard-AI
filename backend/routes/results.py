from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db import models
from services.mitigation_service import get_evaluation_matrix

router = APIRouter()


@router.get("/logs")
def get_logs(limit: int = 50, db: Session = Depends(get_db)):
    rows = (
        db.query(models.AttackResult)
        .order_by(models.AttackResult.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "payload_id": r.payload_id,
            "category": r.category,
            "payload": r.payload,
            "llm_response": r.llm_response,
            "success": r.success,
            "mitigation_active": r.mitigation_active,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in rows
    ]


@router.get("/matrix")
def get_matrix():
    return get_evaluation_matrix()


@router.delete("/clear")
def clear_logs(db: Session = Depends(get_db)):
    db.query(models.AttackResult).delete()
    db.commit()
    return {"status": "logs cleared"}
