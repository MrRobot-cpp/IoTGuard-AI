from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from typing import TYPE_CHECKING, Any

from ..device_state import DeviceStateManager
from ..models import AlarmState, DoorState, SensorReading
from ..store import EventStore

if TYPE_CHECKING:
    from ..hub import SimulationHub

log = logging.getLogger(__name__)

OLLAMA_CHAT_URL = "http://127.0.0.1:11434/api/chat"

DEFAULT_SENSOR_GOAL = (
    "Manage the home from current sensor readings. Rules: "
    "smoke index >= 35 → set alarm armed_home if disarmed, or triggered if already armed; "
    "send alert email to owner@home.local. "
    "motion true while alarm is armed → turn on hallway light. "
    "temperature > 26°C → turn off living_room light. "
    "temperature < 18°C → turn on living_room light. "
    "if alarm is armed_away, door must be closed. "
    "Use minimal safe actions; return [] if nothing is needed."
)

SYSTEM_PROMPT = (
    "You are a home automation policy engine driven by temperature, motion, and smoke sensors. "
    "You ONLY output valid JSON: a JSON array of actions, no prose. "
    "Each action is an object with \"action\" and \"args\". Allowed actions:\n"
    '- {"action":"set_light","args":{"name":"living_room|kitchen|hallway","on":true|false}}\n'
    '- {"action":"set_alarm","args":{"state":"disarmed|armed_home|armed_away|triggered"}}\n'
    '- {"action":"set_door","args":{"state":"open|closed|ajar"}}\n'
    '- {"action":"send_email","args":{"to_addr":"email","subject":"text","body":"text"}}\n'
    "Use only light names and states from context. Prefer minimal, safe changes. "
    "If no change is needed, output []."
)


def ollama_chat_url_from_base(base_url: str) -> str:
    root = base_url.rstrip("/")
    if root.endswith("/v1"):
        root = root[:-3]
    return f"{root}/api/chat"


def _extract_json_array(text: str) -> list[dict[str, Any]]:
    """Parse a JSON array from model output; tolerate ```json fences."""
    s = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", s, re.IGNORECASE)
    if fence:
        s = fence.group(1).strip()
    data = json.loads(s)
    if not isinstance(data, list):
        raise ValueError("expected JSON array of actions")
    out: list[dict[str, Any]] = []
    for item in data:
        if isinstance(item, dict):
            out.append(item)
    return out


def check_ollama_available(ollama_root: str = "http://127.0.0.1:11434", timeout_sec: float = 3.0) -> dict[str, Any]:
    """Ping Ollama /api/tags to verify the daemon is running."""
    root = ollama_root.rstrip("/")
    if root.endswith("/v1"):
        root = root[:-3]
    url = f"{root}/api/tags"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
        models = [m.get("name", "") for m in data.get("models", []) if isinstance(m, dict)]
        return {"ok": True, "url": url, "models": models}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        return {"ok": False, "url": url, "error": str(e)}


def fetch_action_plan_from_ollama(
    *,
    model: str,
    context: dict[str, Any],
    goal: str,
    ollama_url: str = OLLAMA_CHAT_URL,
    timeout_sec: float = 120.0,
) -> list[dict[str, Any]]:
    """
    Ask a local Ollama model for a machine-readable action plan.

    Requires Ollama running (default http://127.0.0.1:11434).
    """
    user = json.dumps({"goal": goal, "context": context}, default=str)
    body = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ],
    }
    req = urllib.request.Request(
        ollama_url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            raw = json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.URLError as e:
        raise RuntimeError(
            "Could not reach Ollama. Install from https://ollama.com, run "
            "`ollama serve`, then `ollama pull <model>`."
        ) from e

    msg = raw.get("message") or {}
    content = msg.get("content") or ""
    if not content.strip():
        raise RuntimeError(f"empty model response: {raw!r}")
    return _extract_json_array(content)


def reading_to_dict(reading: SensorReading) -> dict[str, Any]:
    return {
        "sensor_id": reading.sensor_id,
        "sensor_type": reading.sensor_type,
        "value": reading.value,
        "unit": reading.unit,
        "metadata": reading.metadata,
        "ts": reading.ts.isoformat(),
    }


def build_context(devices: DeviceStateManager, store: EventStore | None, *, sensor_limit: int = 20) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "devices": devices.snapshot(),
        "known_lights": list(devices.get_lights().keys()),
    }
    if store is not None:
        ctx["recent_sensor_events"] = store.recent_sensor_events(sensor_limit)
        ctx["recent_actions"] = store.recent_actions(10)
    return ctx


def build_sensor_context(
    hub: SimulationHub,
    *,
    current_readings: list[SensorReading] | None = None,
    sensor_limit: int = 20,
) -> dict[str, Any]:
    ctx = build_context(hub.devices, hub.store, sensor_limit=sensor_limit)
    readings = current_readings or []
    ctx["current_readings"] = [reading_to_dict(r) for r in readings]
    ctx["sensor_policy"] = {
        "smoke_threshold": 35,
        "temperature_comfort_c": [18, 26],
        "motion_sensor_id": hub.motion.sensor_id,
        "temperature_sensor_id": hub.temperature.sensor_id,
        "smoke_sensor_id": hub.smoke.sensor_id,
    }
    ctx["calendar_upcoming"] = [
        {
            "title": e.title,
            "start": e.start.isoformat(),
            "end": e.end.isoformat(),
            "location": e.location,
        }
        for e in hub.calendar.upcoming(24)
    ]
    return ctx


def apply_action_plan(
    devices: DeviceStateManager,
    plan: list[dict[str, Any]],
    *,
    hub: SimulationHub | None = None,
) -> list[dict[str, Any]]:
    """Execute allowlisted actions; returns a list of result dicts."""
    allowed_lights = set(devices.get_lights().keys())
    results: list[dict[str, Any]] = []

    for step in plan:
        action = step.get("action")
        args = step.get("args") if isinstance(step.get("args"), dict) else {}

        if action == "set_light":
            name = str(args.get("name", ""))
            if name not in allowed_lights:
                results.append({"action": action, "ok": False, "error": f"unknown light {name!r}"})
                continue
            on = bool(args.get("on"))
            devices.set_light(name, on)
            results.append({"action": action, "ok": True, "args": {"name": name, "on": on}})
        elif action == "set_alarm":
            try:
                st = AlarmState(str(args.get("state", "")))
            except ValueError:
                results.append({"action": action, "ok": False, "error": "invalid alarm state"})
                continue
            devices.set_alarm(st)
            results.append({"action": action, "ok": True, "args": {"state": st.value}})
        elif action == "set_door":
            try:
                st = DoorState(str(args.get("state", "")))
            except ValueError:
                results.append({"action": action, "ok": False, "error": "invalid door state"})
                continue
            devices.set_door(st)
            results.append({"action": action, "ok": True, "args": {"state": st.value}})
        elif action == "send_email":
            if hub is None:
                results.append({"action": action, "ok": False, "error": "email not available"})
                continue
            to_addr = str(args.get("to_addr", "owner@home.local"))
            subject = str(args.get("subject", "Sensor alert"))
            body = str(args.get("body", ""))
            msg = hub.email.send(to_addr, subject, body)
            results.append(
                {
                    "action": action,
                    "ok": True,
                    "args": {"to_addr": to_addr, "subject": subject, "message_id": msg.message_id},
                }
            )
        else:
            results.append({"action": str(action), "ok": False, "error": "unknown action"})

    return results
