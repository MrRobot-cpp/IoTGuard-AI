from __future__ import annotations

import json
from pathlib import Path

import pytest

from simulation.device_state import DeviceStateManager
from simulation.hub import SimulationHub
from simulation.integrations.simulated import CalendarSimulator, EmailSimulator, WebFetchSimulator
from simulation.models import AlarmState, DoorState
from simulation.sensors.simulator import MotionDetector, SmokeDetector, TemperatureSensor
from simulation.store import EventStore


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_sim.db"


def test_temperature_sensor_stable_range():
    s = TemperatureSensor("t1", seed=1)
    for _ in range(20):
        r = s.read()
        assert r.sensor_type == "temperature"
        assert 15.0 <= float(r.value) <= 32.0


def test_motion_and_smoke_types():
    m = MotionDetector("m1", seed=2)
    assert m.read().sensor_type == "motion"
    s = SmokeDetector("s1", seed=3)
    assert s.read().sensor_type == "smoke"


def test_event_store_roundtrip(db_path: Path):
    store = EventStore(db_path)
    reading = TemperatureSensor("t1", seed=0).read()
    action_id = store.record_sensor_event(reading)
    assert action_id >= 1

    mgr = DeviceStateManager(store=store)
    mgr.set_light("living_room", True)
    events = store.recent_sensor_events(5)
    actions = store.recent_actions(5)
    assert len(events) >= 1
    assert len(actions) >= 1
    assert json.loads(events[0]["value"]) == reading.value


def test_device_state_manager(db_path: Path):
    store = EventStore(db_path)
    mgr = DeviceStateManager(store=store, door=DoorState.CLOSED, alarm=AlarmState.DISARMED)
    mgr.set_door(DoorState.OPEN)
    mgr.set_alarm(AlarmState.ARMED_AWAY)
    mgr.set_light("kitchen", True)
    snap = mgr.snapshot()
    assert snap["door"] == "open"
    assert snap["alarm"] == "armed_away"
    assert snap["lights"]["kitchen"] is True


def test_integrations():
    email = EmailSimulator()
    msg = email.send("a@b.com", "Hi", "Body")
    assert msg.message_id
    assert len(email.list_outbox()) == 1

    cal = CalendarSimulator()
    cal.seed_demo()
    assert len(cal.upcoming(48)) >= 1

    web = WebFetchSimulator(allow_network=False)
    body = web.fetch("https://example.com")
    assert body["simulated"] is True
    assert "text" in body


def test_hub_poll_persists(db_path: Path):
    hub = SimulationHub(db_path, seed=99)
    readings = hub.poll_sensors()
    assert len(readings) == 3
    assert len(hub.store.recent_sensor_events(10)) == 3


def test_simulation_api():
    from fastapi.testclient import TestClient

    from main import app

    c = TestClient(app)
    r = c.get("/simulation/state")
    assert r.status_code == 200
    assert "devices" in r.json()

    r = c.post("/simulation/sensors/poll")
    assert r.status_code == 200
    assert len(r.json()["readings"]) == 3

    r = c.post("/simulation/devices/lights/living_room", json={"on": True})
    assert r.status_code == 200

    r = c.post(
        "/simulation/integrations/email",
        json={"to_addr": "x@y.com", "subject": "t", "body": "b"},
    )
    assert r.status_code == 200

    r = c.get("/simulation/integrations/fetch", params={"url": "https://example.com"})
    assert r.status_code == 200
    assert r.json()["simulated"] is True
