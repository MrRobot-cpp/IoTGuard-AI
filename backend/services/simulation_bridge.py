from __future__ import annotations

from dataclasses import dataclass

from core.devices import Device
from core.sensors import SensorReading
from simulation.models import AlarmState, DoorState
from services.simulation_service import get_hub

# Gateway device_id -> simulation light name
_LIGHT_IDS: dict[str, str] = {
    "light_living": "living_room",
    "light_bedroom": "kitchen",
    "light_hallway": "hallway",
}

_thermostat_target_c: float = 21.0


def _alarm_to_state(alarm: AlarmState) -> dict[str, bool]:
    return {
        "armed": alarm in (AlarmState.ARMED_HOME, AlarmState.ARMED_AWAY, AlarmState.TRIGGERED),
        "triggered": alarm == AlarmState.TRIGGERED,
    }


def _door_to_lock(door: DoorState) -> dict[str, bool | str]:
    return {
        "locked": door == DoorState.CLOSED,
        "ajar": door == DoorState.AJAR,
        "state": door.value,
    }


def get_all_devices() -> list[Device]:
    hub = get_hub()
    snap = hub.devices.snapshot()
    lights = snap["lights"]
    alarm = AlarmState(snap["alarm"])
    door = DoorState(snap["door"])
    temp = hub.temperature.read().value
    motion = hub.motion.read().value

    return [
        Device("light_living", "Living Room Light", "light", {"on": lights.get("living_room", False)}),
        Device("light_bedroom", "Kitchen Light", "light", {"on": lights.get("kitchen", False)}),
        Device("light_hallway", "Hallway Light", "light", {"on": lights.get("hallway", False)}),
        Device("lock_front", "Front Door", "lock", _door_to_lock(door)),
        Device("lock_garage", "Garage Lock", "lock", {"locked": True}),
        Device(
            "thermostat",
            "Main Thermostat",
            "thermostat",
            {"temp_c": round(float(temp), 1), "target_c": _thermostat_target_c, "mode": "auto"},
        ),
        Device(
            "camera_front",
            "Front Camera",
            "camera",
            {"recording": True, "motion": bool(motion)},
        ),
        Device("alarm", "Security Alarm", "alarm", _alarm_to_state(alarm)),
    ]


def update_device_state(device_id: str, **kwargs) -> Device | None:
    hub = get_hub()
    global _thermostat_target_c

    with hub.devices.action_source("gateway_agent"):
        if device_id in _LIGHT_IDS and "on" in kwargs:
            hub.devices.set_light(_LIGHT_IDS[device_id], bool(kwargs["on"]))
        elif device_id == "lock_front":
            if kwargs.get("locked") is True:
                hub.devices.set_door(DoorState.CLOSED)
            elif kwargs.get("locked") is False:
                hub.devices.set_door(DoorState.OPEN)
        elif device_id == "alarm":
            if kwargs.get("triggered"):
                hub.devices.set_alarm(AlarmState.TRIGGERED)
            elif kwargs.get("armed") is True:
                hub.devices.set_alarm(AlarmState.ARMED_HOME)
            elif kwargs.get("armed") is False:
                hub.devices.set_alarm(AlarmState.DISARMED)
        elif device_id == "thermostat" and "temp_c" in kwargs:
            _thermostat_target_c = float(kwargs["temp_c"])
        else:
            return None

    for d in get_all_devices():
        if d.id == device_id:
            return d
    return None


def reset_all_devices() -> None:
    global _thermostat_target_c
    hub = get_hub()
    _thermostat_target_c = 21.0
    with hub.devices.action_source("gateway_agent"):
        hub.devices.set_door(DoorState.CLOSED)
        hub.devices.set_alarm(AlarmState.DISARMED)
        for name in hub.devices.get_lights():
            hub.devices.set_light(name, False)


def get_sensor_readings(*, inject: str | None = None, poll: bool = True) -> list[SensorReading]:
    hub = get_hub()
    if poll:
        raw = hub.poll_sensors()
    else:
        raw = [hub.temperature.read(), hub.motion.read(), hub.smoke.read()]

    readings = [
        SensorReading(r.sensor_id, r.sensor_type, r.value, r.unit or "")
        for r in raw
    ]
    snap = hub.devices.snapshot()
    readings.append(
        SensorReading("door_sensor", "contact", snap["door"], "")
    )
    if inject:
        readings.append(SensorReading("spoofed", "external_data", inject, ""))
    return readings


def simulation_summary() -> dict:
    hub = get_hub()
    return {
        "devices": hub.devices.snapshot(),
        "integrations": {
            "email_outbox": len(hub.email.list_outbox(100)),
            "calendar_upcoming": len(hub.calendar.upcoming(24)),
        },
        "recent_sensor_events": hub.store.recent_sensor_events(10),
        "recent_actions": hub.store.recent_actions(10),
    }
