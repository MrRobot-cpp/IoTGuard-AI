"""Gateway ↔ simulation hub integration tests."""

from fastapi.testclient import TestClient

from main import app
from services.simulation_service import get_hub


def test_gateway_devices_match_simulation_hub():
    hub = get_hub()
    with hub.devices.action_source("test"):
        hub.devices.set_light("living_room", True)

    c = TestClient(app)
    devices = {d["id"]: d for d in c.get("/gateway/devices").json()}
    assert devices["light_living"]["state"]["on"] is True
    assert c.get("/simulation/state").json()["devices"]["lights"]["living_room"] is True


def test_gateway_sensors_use_simulation_types():
    c = TestClient(app)
    readings = c.get("/gateway/sensors", params={"poll": True}).json()
    types = {r["type"] for r in readings}
    assert "temperature" in types
    assert "motion" in types
    assert "smoke" in types


def test_tool_call_updates_simulation_hub():
    from core.tools import execute_tool

    hub = get_hub()
    with hub.devices.action_source("test"):
        hub.devices.set_light("living_room", False)

    execute_tool("turn_on", {"device_id": "light_living"})
    assert hub.devices.get_lights()["living_room"] is True
