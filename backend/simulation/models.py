from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DoorState(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    AJAR = "ajar"


class AlarmState(str, Enum):
    DISARMED = "disarmed"
    ARMED_HOME = "armed_home"
    ARMED_AWAY = "armed_away"
    TRIGGERED = "triggered"


@dataclass
class SensorReading:
    sensor_id: str
    sensor_type: str
    value: Any
    unit: str | None
    metadata: dict[str, Any] = field(default_factory=dict)
    ts: datetime = field(default_factory=utc_now)


@dataclass
class ExecutedAction:
    action_type: str
    payload: dict[str, Any]
    source: str
    success: bool
    ts: datetime = field(default_factory=utc_now)
    error: str | None = None
