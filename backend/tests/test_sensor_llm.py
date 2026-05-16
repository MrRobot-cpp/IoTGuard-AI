from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from simulation.hub import SimulationHub
from simulation.llm.local_brain import apply_action_plan, build_sensor_context, ollama_chat_url_from_base
from services.sensor_llm_service import run_sensor_llm_cycle


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "llm_test.db"


def test_ollama_chat_url_from_base():
    assert ollama_chat_url_from_base("http://localhost:11434/v1") == "http://localhost:11434/api/chat"
    assert ollama_chat_url_from_base("http://127.0.0.1:11434") == "http://127.0.0.1:11434/api/chat"


def test_apply_action_plan_lights_and_email(db_path):
    hub = SimulationHub(db_path, seed=1)
    plan = [
        {"action": "set_light", "args": {"name": "hallway", "on": True}},
        {
            "action": "send_email",
            "args": {"to_addr": "a@b.com", "subject": "Alert", "body": "motion"},
        },
    ]
    results = apply_action_plan(hub.devices, plan, hub=hub)
    assert results[0]["ok"] is True
    assert results[1]["ok"] is True
    assert hub.devices.get_lights()["hallway"] is True
    assert len(hub.email.list_outbox()) == 1


def test_build_sensor_context(db_path):
    hub = SimulationHub(db_path, seed=2)
    readings = hub.poll_sensors()
    ctx = build_sensor_context(hub, current_readings=readings)
    assert len(ctx["current_readings"]) == 3
    assert "sensor_policy" in ctx
    assert ctx["devices"]["door"] == "closed"


@patch("services.sensor_llm_service.fetch_action_plan_from_ollama")
def test_run_sensor_llm_cycle_mocked(mock_fetch, db_path):
    mock_fetch.return_value = [{"action": "set_light", "args": {"name": "kitchen", "on": True}}]
    hub = SimulationHub(db_path, seed=3)
    out = run_sensor_llm_cycle(hub, poll_sensors_first=True, apply_plan=True)
    assert mock_fetch.called
    assert out["plan"][0]["action"] == "set_light"
    assert out["results"][0]["ok"] is True
    assert hub.devices.get_lights()["kitchen"] is True


@patch("services.sensor_llm_service.fetch_action_plan_from_ollama")
def test_llm_manage_api(mock_fetch):
    from fastapi.testclient import TestClient

    from main import app

    mock_fetch.return_value = []
    client = TestClient(app)
    r = client.get("/simulation/llm/health")
    assert r.status_code == 200
    assert "ok" in r.json()

    r = client.post(
        "/simulation/llm/manage",
        json={"poll_sensors_first": True, "apply_plan": True},
    )
    assert r.status_code == 200
    assert "plan" in r.json()
