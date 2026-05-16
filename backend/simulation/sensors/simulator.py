from __future__ import annotations

import random
import time
from abc import ABC, abstractmethod
from typing import Callable

from ..models import SensorReading, utc_now


class Sensor(ABC):
    def __init__(self, sensor_id: str) -> None:
        self.sensor_id = sensor_id

    @abstractmethod
    def read(self) -> SensorReading:
        raise NotImplementedError


class TemperatureSensor(Sensor):
    """Simulated indoor temperature with gentle drift."""

    def __init__(
        self,
        sensor_id: str = "temp-1",
        *,
        base_c: float = 22.0,
        noise: float = 0.3,
        seed: int | None = None,
    ) -> None:
        super().__init__(sensor_id)
        self._rng = random.Random(seed)
        self._current = base_c + self._rng.uniform(-noise, noise)
        self._noise = noise

    def read(self) -> SensorReading:
        drift = self._rng.uniform(-0.15, 0.15)
        self._current = max(15.0, min(32.0, self._current + drift))
        value = round(self._current, 2)
        return SensorReading(
            sensor_id=self.sensor_id,
            sensor_type="temperature",
            value=value,
            unit="C",
            metadata={"simulated": True},
            ts=utc_now(),
        )


class MotionDetector(Sensor):
    """Simulated PIR-style motion (random occupancy bursts)."""

    def __init__(
        self,
        sensor_id: str = "motion-1",
        *,
        occupancy_probability: float = 0.25,
        seed: int | None = None,
    ) -> None:
        super().__init__(sensor_id)
        self._rng = random.Random(seed)
        self._p = occupancy_probability

    def read(self) -> SensorReading:
        motion = self._rng.random() < self._p
        return SensorReading(
            sensor_id=self.sensor_id,
            sensor_type="motion",
            value=motion,
            unit=None,
            metadata={"simulated": True},
            ts=utc_now(),
        )


class SmokeDetector(Sensor):
    """Simulated smoke / particulate level (normally low)."""

    def __init__(
        self, sensor_id: str = "smoke-1", *, false_alarm_rate: float = 0.02, seed: int | None = None
    ) -> None:
        super().__init__(sensor_id)
        self._rng = random.Random(seed)
        self._false_alarm_rate = false_alarm_rate

    def read(self) -> SensorReading:
        if self._rng.random() < self._false_alarm_rate:
            level = self._rng.uniform(40, 95)
        else:
            level = self._rng.uniform(0, 15)
        return SensorReading(
            sensor_id=self.sensor_id,
            sensor_type="smoke",
            value=round(level, 1),
            unit="index",
            metadata={"simulated": True, "threshold": 35},
            ts=utc_now(),
        )


def run_polling_loop(
    sensors: list[tuple[Sensor, Callable[[SensorReading], None]]],
    *,
    interval_sec: float = 1.0,
    iterations: int | None = None,
) -> None:
    n = 0
    while iterations is None or n < iterations:
        for sensor, handler in sensors:
            handler(sensor.read())
        time.sleep(interval_sec)
        n += 1
