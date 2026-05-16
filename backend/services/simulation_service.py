from __future__ import annotations

from pathlib import Path

from simulation.hub import SimulationHub

_hub: SimulationHub | None = None

_DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "simulation_events.db"


def init_simulation_hub(db_path: Path | None = None, *, seed: int | None = 42) -> SimulationHub:
    global _hub
    _hub = SimulationHub(db_path or _DEFAULT_DB, seed=seed)
    return _hub


def get_hub() -> SimulationHub:
    if _hub is None:
        return init_simulation_hub()
    return _hub
