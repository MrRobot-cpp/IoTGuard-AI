from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .device_state import DeviceStateManager
from .integrations.simulated import CalendarSimulator, EmailSimulator, WebFetchSimulator
from .models import AlarmState, DoorState, SensorReading
from .sensors.simulator import MotionDetector, SmokeDetector, TemperatureSensor
from .store import EventStore

log = logging.getLogger(__name__)


class SimulationHub:
    """Orchestrates sensors, device state, integrations, and SQLite event storage."""

    def __init__(self, db_path: str | Path, *, seed: int | None = 42) -> None:
        self.store = EventStore(db_path)
        self.devices = DeviceStateManager(store=self.store)
        self.temperature = TemperatureSensor("temp-1", seed=seed)
        self.motion = MotionDetector("motion-1", seed=seed)
        self.smoke = SmokeDetector("smoke-1", seed=seed)
        self.email = EmailSimulator()
        self.calendar = CalendarSimulator()
        self.calendar.seed_demo()
        self.web = WebFetchSimulator(allow_network=False)

    def poll_sensors(self) -> list[SensorReading]:
        readings = [self.temperature.read(), self.motion.read(), self.smoke.read()]
        for reading in readings:
            self.store.record_sensor_event(reading)
            self._react_to_reading(reading)
        return readings

    def _react_to_reading(self, reading: SensorReading) -> None:
        if reading.sensor_type == "smoke":
            threshold = float(reading.metadata.get("threshold", 35))
            if isinstance(reading.value, (int, float)) and reading.value >= threshold:
                log.warning("smoke threshold exceeded: %s", reading.value)
                self.devices.trigger_alarm_if_armed(f"smoke level {reading.value}")
        elif reading.sensor_type == "motion" and reading.value is True:
            if self.devices.door == DoorState.OPEN and self.devices.alarm in (
                AlarmState.ARMED_HOME,
                AlarmState.ARMED_AWAY,
            ):
                self.devices.trigger_alarm_if_armed("motion while door open and alarm armed")

    def snapshot(self) -> dict[str, Any]:
        return {
            "devices": self.devices.snapshot(),
            "integrations": {
                "email_outbox_count": len(self.email._outbox),
                "calendar_events": len(self.calendar._events),
            },
        }
