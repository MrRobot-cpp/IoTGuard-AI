from dataclasses import dataclass, field
from typing import Any


@dataclass
class Device:
    id: str
    name: str
    type: str  # light | lock | thermostat | camera | alarm
    state: dict[str, Any] = field(default_factory=dict)
    online: bool = True


def get_all() -> list[Device]:
    from services.simulation_bridge import get_all_devices

    return get_all_devices()


def get(device_id: str) -> Device | None:
    for d in get_all():
        if d.id == device_id:
            return d
    return None


def update_state(device_id: str, **kwargs) -> Device | None:
    from services.simulation_bridge import update_device_state

    return update_device_state(device_id, **kwargs)


def reset_all() -> None:
    from services.simulation_bridge import reset_all_devices

    reset_all_devices()
