from dataclasses import dataclass


@dataclass
class SensorReading:
    sensor_id: str
    type: str
    value: float | str | bool
    unit: str = ""


def get_readings(inject: str | None = None, *, poll: bool = True) -> list[SensorReading]:
    """Simulated sensors via SimulationHub (temperature, motion, smoke, door)."""
    from services.simulation_bridge import get_sensor_readings

    return get_sensor_readings(inject=inject, poll=poll)
