#!/usr/bin/env python3
"""Quick project health checklist."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from services.sensor_llm_service import ollama_health


def main() -> None:
    checks: list[tuple[str, bool, str]] = []
    c = TestClient(app)

    h = ollama_health()
    model_count = len(h.get("models", []))
    checks.append(("Ollama daemon", h.get("ok", False), f"{model_count} model(s)"))
    checks.append(("Ollama model pulled", model_count > 0, "run: ollama pull llama3.2"))

    r = c.get("/health")
    checks.append(("API /health", r.status_code == 200, str(r.json())))

    r = c.get("/simulation/state")
    checks.append(("Simulation /state", r.status_code == 200, "ok"))

    r = c.post("/simulation/sensors/poll")
    n = len(r.json().get("readings", []))
    checks.append(("Sensors (temp/motion/smoke)", r.status_code == 200 and n == 3, f"{n} readings"))

    r = c.get("/gateway/devices")
    checks.append(("Gateway devices", r.status_code == 200, f"{len(r.json())} devices"))

    r = c.get("/gateway/sensors", params={"poll": True})
    body = r.json()
    types = {x.get("type") for x in body} if isinstance(body, list) else set()
    checks.append(
        (
            "Gateway sensors (simulation)",
            r.status_code == 200 and "temperature" in types,
            f"types={types}",
        )
    )

    r = c.get("/gateway/simulation")
    checks.append(("Gateway + simulation summary", r.status_code == 200, "linked"))

    print("IoTGuard-AI — Project Health")
    print("=" * 50)
    fails = 0
    for name, ok, detail in checks:
        mark = "YES" if ok else "NO "
        if not ok:
            fails += 1
        print(f"[{mark}] {name} — {detail}")
    print("=" * 50)
    if fails:
        print(f"{fails} item(s) need attention (see NO above).")
        sys.exit(1)
    print("All listed checks passed.")


if __name__ == "__main__":
    main()
