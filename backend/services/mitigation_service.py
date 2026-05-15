from db.database import SessionLocal
from db import models
from sqlalchemy import func


def get_evaluation_matrix() -> list[dict]:
    """
    Build the before/after evaluation matrix from stored results.
    Returns rows grouped by (mitigation, category).
    """
    db = SessionLocal()
    rows = (
        db.query(
            models.AttackResult.mitigation_active,
            models.AttackResult.category,
            func.count(models.AttackResult.id).label("total"),
            func.sum(models.AttackResult.success.cast(models.AttackResult.success.type)).label("successes"),
        )
        .group_by(models.AttackResult.mitigation_active, models.AttackResult.category)
        .all()
    )
    db.close()

    matrix = []
    for row in rows:
        total = row.total or 0
        successes = int(row.successes or 0)
        matrix.append({
            "mitigation": row.mitigation_active,
            "category": row.category,
            "total": total,
            "attack_successes": successes,
            "attack_success_rate": round(successes / total, 2) if total else 0.0,
            "blocked": total - successes,
            "block_rate": round((total - successes) / total, 2) if total else 0.0,
        })

    return matrix
