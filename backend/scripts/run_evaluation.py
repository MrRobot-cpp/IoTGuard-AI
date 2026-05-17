"""
Run all 24 attacks x 4 mitigations and save results to JSON.
Safe to re-run — skips combinations already in the output file.

Usage (from backend/):
    python scripts/run_evaluation.py
    python scripts/run_evaluation.py --out ../notebooks/eval_results.json
"""

import sys, os, json, time, argparse
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from db.database import init_db
from services.simulation_service import init_simulation_hub
from services.attack_service import run_all

MITIGATIONS = ["none", "input_filter", "privilege_separation", "llm_detector"]
OUT_DEFAULT = BACKEND_ROOT.parent / "notebooks" / "eval_results.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(OUT_DEFAULT))
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing results so we can skip already-done mitigations
    if out_path.exists():
        with open(out_path) as f:
            results = json.load(f)
        print(f"Loaded existing results from {out_path}")
    else:
        results = {}

    init_db()
    init_simulation_hub()

    for mit in MITIGATIONS:
        if mit in results:
            print(f"[SKIP] {mit} — already done ({len(results[mit])} results)")
            continue

        print(f"\n[RUN] mitigation={mit} ...", flush=True)
        t0 = time.time()

        try:
            mit_results = run_all(category=None, mitigation=mit, use_judge=False)
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

        elapsed = round(time.time() - t0)
        succeeded = sum(1 for r in mit_results if r.get("success"))
        blocked   = sum(1 for r in mit_results if r.get("blocked"))

        results[mit] = mit_results

        # Save after every mitigation so progress is never lost
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"  Done in {elapsed}s — {succeeded}/24 succeeded, {blocked}/24 blocked")
        print(f"  Saved to {out_path}")

    print(f"\nAll mitigations complete. Results at: {out_path}")


if __name__ == "__main__":
    main()
