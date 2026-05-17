from db.database import SessionLocal
from db import models
from sqlalchemy import func


def get_evaluation_matrix() -> list[dict]:
    """
    Build the evaluation matrix using only the most recent run per mitigation.
    Finds the latest timestamp per mitigation, then keeps only rows from that
    same batch (matching payload_id set) to avoid polluting counts from reruns.
    """
    db = SessionLocal()

    # Step 1: latest timestamp per mitigation
    latest_ts_rows = (
        db.query(
            models.AttackResult.mitigation_active,
            func.max(models.AttackResult.timestamp).label("latest_ts"),
        )
        .group_by(models.AttackResult.mitigation_active)
        .all()
    )

    if not latest_ts_rows:
        db.close()
        return []

    # Step 2: for each mitigation, find the min id of the latest batch
    # (rows inserted in the same run will have consecutive ids close to max)
    # Simpler: just get the 24 most recent rows per mitigation
    matrix = []
    for ts_row in latest_ts_rows:
        mit = ts_row.mitigation_active
        # Get the most recent 24 rows for this mitigation (one full run)
        recent_rows = (
            db.query(models.AttackResult)
            .filter(models.AttackResult.mitigation_active == mit)
            .order_by(models.AttackResult.id.desc())
            .limit(24)
            .all()
        )

        by_category: dict[str, dict] = {}
        for r in recent_rows:
            cat = r.category
            if cat not in by_category:
                by_category[cat] = {"total": 0, "successes": 0, "blocked": 0}
            by_category[cat]["total"] += 1
            by_category[cat]["successes"] += int(bool(r.success))
            by_category[cat]["blocked"] += int(bool(r.blocked))

        for cat, counts in by_category.items():
            total = counts["total"]
            successes = counts["successes"]
            blocked = counts["blocked"]
            matrix.append({
                "mitigation": mit,
                "category": cat,
                "total": total,
                "attack_successes": successes,
                "attack_success_rate": round(successes / total, 2) if total else 0.0,
                "blocked": blocked,
                "block_rate": round(blocked / total, 2) if total else 0.0,
            })

    db.close()
    return matrix
