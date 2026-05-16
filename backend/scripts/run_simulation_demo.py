#!/usr/bin/env python3
"""CLI demo: poll sensors, show device state, and print stored events."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Allow running as: python scripts/run_simulation_demo.py from backend/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.simulation_service import init_simulation_hub  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="IoTGuard sensor simulation demo")
    parser.add_argument("--polls", type=int, default=5, help="number of sensor poll cycles")
    parser.add_argument("--interval", type=float, default=0.5, help="seconds between polls")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    import time

    from simulation.models import AlarmState

    hub = init_simulation_hub(seed=args.seed)
    hub.devices.set_alarm(AlarmState.ARMED_HOME)

    print("=== Initial state ===")
    print(json.dumps(hub.snapshot(), indent=2))

    hub.email.send("owner@home.local", "Simulation started", "Demo run active.")
    print("\n=== Calendar (next 24h) ===")
    for ev in hub.calendar.upcoming():
        print(f"  {ev.start.isoformat()} — {ev.title} @ {ev.location or 'n/a'}")

    print(f"\n=== Polling sensors ({args.polls}x) ===")
    for i in range(args.polls):
        readings = hub.poll_sensors()
        print(f"\n--- Poll {i + 1} ---")
        for r in readings:
            print(f"  {r.sensor_id} ({r.sensor_type}): {r.value} {r.unit or ''}")
        print(f"  devices: {hub.devices.snapshot()}")
        if i < args.polls - 1:
            time.sleep(args.interval)

    print("\n=== Web fetch (simulated) ===")
    print(json.dumps(hub.web.fetch("https://example.com/status"), indent=2)[:400])

    print("\n=== Recent sensor events (DB) ===")
    for row in hub.store.recent_sensor_events(10):
        print(f"  #{row['id']} {row['sensor_type']}={row['value']} @ {row['ts']}")

    print("\n=== Recent actions (DB) ===")
    for row in hub.store.recent_actions(10):
        print(f"  #{row['id']} {row['action_type']} ok={row['success']} {row['payload_json']}")


if __name__ == "__main__":
    main()
