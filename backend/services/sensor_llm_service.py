from __future__ import annotations

from typing import Any

from config import settings
from simulation.hub import SimulationHub
from simulation.llm.local_brain import (
    DEFAULT_SENSOR_GOAL,
    apply_action_plan,
    build_sensor_context,
    check_ollama_available,
    fetch_action_plan_from_ollama,
    ollama_chat_url_from_base,
)
from services.simulation_service import get_hub


def _chat_url() -> str:
    if settings.ollama_chat_url.strip():
        return settings.ollama_chat_url.strip()
    return ollama_chat_url_from_base(settings.ollama_base_url)


def ollama_health() -> dict[str, Any]:
    root = settings.ollama_base_url.rstrip("/").removesuffix("/v1")
    return check_ollama_available(root, timeout_sec=5.0)


def run_sensor_llm_cycle(
    hub: SimulationHub | None = None,
    *,
    goal: str | None = None,
    poll_sensors_first: bool = True,
    apply_plan: bool = True,
    model: str | None = None,
) -> dict[str, Any]:
    """
    Poll sensors (optional), ask Ollama for an action plan, optionally apply it.
    """
    hub = hub or get_hub()
    goal = goal or DEFAULT_SENSOR_GOAL
    model = model or settings.ollama_model

    readings = hub.poll_sensors() if poll_sensors_first else []
    context = build_sensor_context(hub, current_readings=readings)

    plan = fetch_action_plan_from_ollama(
        model=model,
        context=context,
        goal=goal,
        ollama_url=_chat_url(),
        timeout_sec=settings.ollama_timeout_sec,
    )

    results: list[dict[str, Any]] = []
    if apply_plan and plan:
        with hub.devices.action_source("ollama"):
            results = apply_action_plan(hub.devices, plan, hub=hub)

    return {
        "model": model,
        "goal": goal,
        "readings": [
            {
                "sensor_id": r.sensor_id,
                "sensor_type": r.sensor_type,
                "value": r.value,
                "unit": r.unit,
            }
            for r in readings
        ],
        "context_summary": {
            "devices": context["devices"],
            "current_readings": context.get("current_readings", []),
        },
        "plan": plan,
        "results": results,
        "devices": hub.devices.snapshot(),
    }


def plan_only(
    hub: SimulationHub | None = None,
    *,
    goal: str | None = None,
    poll_sensors_first: bool = True,
    model: str | None = None,
) -> dict[str, Any]:
    """Return Ollama plan without applying device changes."""
    return run_sensor_llm_cycle(
        hub,
        goal=goal,
        poll_sensors_first=poll_sensors_first,
        apply_plan=False,
        model=model,
    )
