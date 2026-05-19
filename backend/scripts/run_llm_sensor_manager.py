#!/usr/bin/env python3
"""Run one Ollama sensor-management cycle (requires Ollama + pulled model)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings  # noqa: E402
from services.sensor_llm_service import ollama_health, run_sensor_llm_cycle  # noqa: E402
from services.simulation_service import init_simulation_hub  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Ollama local LLM sensor manager")
    parser.add_argument("--goal", type=str, default=None, help="override automation goal")
    parser.add_argument("--model", type=str, default=None, help=f"default: {settings.ollama_model}")
    parser.add_argument("--no-poll", action="store_true", help="skip sensor poll before LLM")
    parser.add_argument("--dry-run", action="store_true", help="plan only, do not apply actions")
    args = parser.parse_args()

    health = ollama_health()
    if not health.get("ok"):
        print("Ollama is not reachable:", health.get("error", health))
        print("Install: https://ollama.com  then: ollama serve && ollama pull", settings.ollama_model)
        sys.exit(1)

    print("Ollama OK. Models:", ", ".join(health.get("models", [])[:5]) or "(none listed)")

    init_simulation_hub()
    result = run_sensor_llm_cycle(
        goal=args.goal,
        poll_sensors_first=not args.no_poll,
        apply_plan=not args.dry_run,
        model=args.model,
    )
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
