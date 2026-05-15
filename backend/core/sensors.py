import random
from dataclasses import dataclass


@dataclass
class SensorReading:
    sensor_id: str
    type: str
    value: float | str | bool
    unit: str = ""


def get_readings(inject: str | None = None) -> list[SensorReading]:
    """Return current simulated sensor readings. If inject is set, append it as a spoofed reading."""
    readings = [
        SensorReading("temp_sensor_1", "temperature", round(random.uniform(18, 25), 1), "°C"),
        SensorReading("humidity_1", "humidity", round(random.uniform(40, 60), 1), "%"),
        SensorReading("motion_front", "motion", random.choice([True, False]), ""),
        SensorReading("smoke_1", "smoke", round(random.uniform(0, 5), 2), "ppm"),
        SensorReading("co2_1", "co2", round(random.uniform(400, 800), 0), "ppm"),
        SensorReading("door_sensor", "contact", random.choice(["open", "closed"]), ""),
    ]

    if inject:
        readings.append(SensorReading("spoofed", "external_data", inject, ""))

    return readings
