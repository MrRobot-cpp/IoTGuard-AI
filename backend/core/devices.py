from dataclasses import dataclass, field
from typing import Any


@dataclass
class Device:
    id: str
    name: str
    type: str           # light | lock | thermostat | camera | alarm
    state: dict[str, Any] = field(default_factory=dict)
    online: bool = True


_registry: dict[str, Device] = {
    "light_living": Device("light_living", "Living Room Light", "light", {"on": False, "brightness": 100}),
    "light_bedroom": Device("light_bedroom", "Bedroom Light", "light", {"on": False, "brightness": 80}),
    "lock_front": Device("lock_front", "Front Door Lock", "lock", {"locked": True}),
    "lock_garage": Device("lock_garage", "Garage Lock", "lock", {"locked": True}),
    "thermostat": Device("thermostat", "Main Thermostat", "thermostat", {"temp_c": 21, "mode": "auto"}),
    "camera_front": Device("camera_front", "Front Camera", "camera", {"recording": True, "motion": False}),
    "alarm": Device("alarm", "Security Alarm", "alarm", {"armed": True, "triggered": False}),
}


def get_all() -> list[Device]:
    return list(_registry.values())


def get(device_id: str) -> Device | None:
    return _registry.get(device_id)


def update_state(device_id: str, **kwargs) -> Device | None:
    device = _registry.get(device_id)
    if not device:
        return None
    device.state.update(kwargs)
    return device


def reset_all():
    for device in _registry.values():
        if device.type == "light":
            device.state = {"on": False, "brightness": 100}
        elif device.type == "lock":
            device.state = {"locked": True}
        elif device.type == "thermostat":
            device.state = {"temp_c": 21, "mode": "auto"}
        elif device.type == "camera":
            device.state = {"recording": True, "motion": False}
        elif device.type == "alarm":
            device.state = {"armed": True, "triggered": False}
