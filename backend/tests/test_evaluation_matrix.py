"""Matrix counts must be mutually exclusive and sum to total."""
from db.database import SessionLocal, init_db
from db import models
from services.mitigation_service import get_evaluation_matrix, EXPECTED_TOTALS


def test_matrix_counts_sum_to_total():
    init_db()
    db = SessionLocal()
    db.query(models.AttackResult).delete()
    db.add_all([
        models.AttackResult(
            payload_id="D01",
            category="direct",
            payload="p1",
            llm_response="blocked",
            success=False,
            blocked=True,
            mitigation_active="input_filter",
        ),
        models.AttackResult(
            payload_id="D02",
            category="direct",
            payload="p2",
            llm_response="unlocked door",
            success=True,
            blocked=False,
            mitigation_active="input_filter",
        ),
        models.AttackResult(
            payload_id="D03",
            category="direct",
            payload="p3",
            llm_response="I cannot help",
            success=False,
            blocked=False,
            mitigation_active="input_filter",
        ),
    ])
    db.commit()
    db.close()

    matrix = get_evaluation_matrix()
    row = next(r for r in matrix if r["mitigation"] == "input_filter" and r["category"] == "direct")
    assert row["total"] == 3
    assert row["attack_successes"] == 1
    assert row["blocked"] == 2
    assert row["mitigation_blocked"] == 1
    assert row["llm_refused"] == 1
    assert row["blocked"] + row["attack_successes"] == row["total"]
    assert row["block_rate"] == round(2 / 3, 2)
    assert row["attack_success_rate"] == round(1 / 3, 2)
    assert row["expected_total"] == EXPECTED_TOTALS["direct"]
