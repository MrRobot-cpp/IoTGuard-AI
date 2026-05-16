from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from simulation.models import AlarmState, DoorState
from services.simulation_service import get_hub
from services import sensor_llm_service

router = APIRouter()


class DoorRequest(BaseModel):
    state: str = Field(..., description="open | closed | ajar")


class AlarmRequest(BaseModel):
    state: str = Field(..., description="disarmed | armed_home | armed_away | triggered")


class LightRequest(BaseModel):
    on: bool


class EmailRequest(BaseModel):
    to_addr: str
    subject: str
    body: str


class CalendarEventRequest(BaseModel):
    title: str
    start: datetime
    duration_minutes: int = 60
    location: str = ""


class LlmManageRequest(BaseModel):
    goal: str | None = Field(
        None,
        description="Natural-language goal for the policy engine; default uses built-in sensor rules",
    )
    poll_sensors_first: bool = True
    apply_plan: bool = True
    model: str | None = None


@router.get("/state")
def get_state():
    hub = get_hub()
    return hub.snapshot()


@router.post("/sensors/poll")
def poll_sensors():
    hub = get_hub()
    readings = hub.poll_sensors()
    return {
        "readings": [
            {
                "sensor_id": r.sensor_id,
                "sensor_type": r.sensor_type,
                "value": r.value,
                "unit": r.unit,
                "metadata": r.metadata,
                "ts": r.ts.isoformat(),
            }
            for r in readings
        ],
        "devices": hub.devices.snapshot(),
    }


@router.get("/sensors/events")
def list_sensor_events(limit: int = Query(50, ge=1, le=500)):
    return get_hub().store.recent_sensor_events(limit)


@router.get("/actions")
def list_actions(limit: int = Query(50, ge=1, le=500)):
    return get_hub().store.recent_actions(limit)


@router.post("/devices/door")
def set_door(req: DoorRequest):
    try:
        state = DoorState(req.state)
    except ValueError as e:
        raise HTTPException(400, f"invalid door state: {req.state}") from e
    get_hub().devices.set_door(state)
    return {"door": state.value}


@router.post("/devices/alarm")
def set_alarm(req: AlarmRequest):
    try:
        state = AlarmState(req.state)
    except ValueError as e:
        raise HTTPException(400, f"invalid alarm state: {req.state}") from e
    get_hub().devices.set_alarm(state)
    return {"alarm": state.value}


@router.post("/devices/lights/{name}")
def set_light(name: str, req: LightRequest):
    hub = get_hub()
    if name not in hub.devices.get_lights():
        raise HTTPException(404, f"unknown light: {name}")
    hub.devices.set_light(name, req.on)
    return {"light": name, "on": req.on}


@router.post("/integrations/email")
def send_email(req: EmailRequest):
    msg = get_hub().email.send(req.to_addr, req.subject, req.body)
    return {
        "message_id": msg.message_id,
        "to_addr": msg.to_addr,
        "subject": msg.subject,
        "sent_at": msg.sent_at.isoformat(),
    }


@router.get("/integrations/email")
def list_emails(limit: int = Query(20, ge=1, le=100)):
    return [
        {
            "message_id": m.message_id,
            "to_addr": m.to_addr,
            "subject": m.subject,
            "body": m.body,
            "sent_at": m.sent_at.isoformat(),
        }
        for m in get_hub().email.list_outbox(limit)
    ]


@router.get("/integrations/calendar")
def list_calendar(within_hours: int = Query(24, ge=1, le=168)):
    return [
        {
            "event_id": e.event_id,
            "title": e.title,
            "start": e.start.isoformat(),
            "end": e.end.isoformat(),
            "location": e.location,
        }
        for e in get_hub().calendar.upcoming(within_hours)
    ]


@router.post("/integrations/calendar")
def add_calendar_event(req: CalendarEventRequest):
    ev = get_hub().calendar.add_event(
        req.title, req.start, req.duration_minutes, req.location
    )
    return {
        "event_id": ev.event_id,
        "title": ev.title,
        "start": ev.start.isoformat(),
        "end": ev.end.isoformat(),
        "location": ev.location,
    }


@router.get("/integrations/fetch")
def fetch_url(url: str = Query(..., min_length=1)):
    return get_hub().web.fetch(url)


@router.get("/llm/health")
def llm_health():
    """Check whether Ollama is reachable and list installed models."""
    return sensor_llm_service.ollama_health()


@router.post("/llm/plan")
def llm_plan(req: LlmManageRequest):
    """Poll sensors and ask Ollama for a JSON action plan (does not apply it)."""
    try:
        return sensor_llm_service.plan_only(
            goal=req.goal,
            poll_sensors_first=req.poll_sensors_first,
            model=req.model,
        )
    except RuntimeError as e:
        raise HTTPException(503, str(e)) from e
    except (ValueError, json.JSONDecodeError) as e:
        raise HTTPException(502, f"invalid model output: {e}") from e


@router.post("/llm/manage")
def llm_manage(req: LlmManageRequest):
    """Poll sensors, get plan from Ollama, and apply device/email actions."""
    try:
        return sensor_llm_service.run_sensor_llm_cycle(
            goal=req.goal,
            poll_sensors_first=req.poll_sensors_first,
            apply_plan=req.apply_plan,
            model=req.model,
        )
    except RuntimeError as e:
        raise HTTPException(503, str(e)) from e
    except (ValueError, json.JSONDecodeError) as e:
        raise HTTPException(502, f"invalid model output: {e}") from e
