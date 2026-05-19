from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Iterator

from .models import AlarmState, DoorState, ExecutedAction, utc_now
from .store import EventStore

log = logging.getLogger(__name__)


class DeviceStateManager:
    """Central door, alarm, and light state with optional persistence of actions."""

    def __init__(
        self,
        store: EventStore | None = None,
        *,
        door: DoorState = DoorState.CLOSED,
        alarm: AlarmState = AlarmState.ARMED_HOME,
        lights: dict[str, bool] | None = None,
        action_source: str = "device_state_manager",
    ) -> None:
        self._store = store
        self._door = door
        self._alarm = alarm
        self._lights: dict[str, bool] = dict(lights or {"living_room": True, "kitchen": True, "hallway": True})
        self._garage_locked: bool = True
        self._action_source = action_source

    def _record_action(self, action_type: str, payload: dict[str, Any], success: bool, error: str | None = None) -> None:
        action = ExecutedAction(
            action_type=action_type,
            payload=payload,
            source=self._action_source,
            success=success,
            ts=utc_now(),
            error=error,
        )
        if self._store:
            self._store.record_action(action)
        log.info("action %s success=%s payload=%s", action_type, success, payload)

    @property
    def door(self) -> DoorState:
        return self._door

    @property
    def alarm(self) -> AlarmState:
        return self._alarm

    def get_lights(self) -> dict[str, bool]:
        return dict(self._lights)

    def set_door(self, state: DoorState) -> None:
        old = self._door
        self._door = state
        self._record_action("set_door", {"from": old.value, "to": state.value}, True)

    def set_alarm(self, state: AlarmState) -> None:
        old = self._alarm
        self._alarm = state
        self._record_action("set_alarm", {"from": old.value, "to": state.value}, True)

    def set_garage(self, locked: bool) -> None:
        self._garage_locked = locked
        self._record_action("set_garage", {"locked": locked}, True)

    @property
    def garage_locked(self) -> bool:
        return self._garage_locked

    def set_light(self, name: str, on: bool) -> None:
        self._lights[name] = on
        self._record_action("set_light", {"light": name, "on": on}, True)

    def trigger_alarm_if_armed(self, reason: str) -> bool:
        if self._alarm in (AlarmState.ARMED_HOME, AlarmState.ARMED_AWAY):
            self._alarm = AlarmState.TRIGGERED
            self._record_action("alarm_triggered", {"reason": reason}, True)
            return True
        self._record_action("alarm_trigger_ignored", {"reason": reason, "alarm_state": self._alarm.value}, True)
        return False

    def snapshot(self) -> dict[str, Any]:
        return {
            "door": self._door.value,
            "alarm": self._alarm.value,
            "lights": dict(self._lights),
            "garage_locked": self._garage_locked,
        }

    @contextmanager
    def action_source(self, source: str) -> Iterator[None]:
        old = self._action_source
        self._action_source = source
        try:
            yield
        finally:
            self._action_source = old
