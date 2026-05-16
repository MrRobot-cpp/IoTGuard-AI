"""Simulated sensors: temperature, motion, smoke."""

from .simulator import MotionDetector, Sensor, SmokeDetector, TemperatureSensor, run_polling_loop

__all__ = [
    "MotionDetector",
    "Sensor",
    "SmokeDetector",
    "TemperatureSensor",
    "run_polling_loop",
]
