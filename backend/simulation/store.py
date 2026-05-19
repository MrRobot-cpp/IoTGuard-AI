from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .models import ExecutedAction, SensorReading


def _serialize_dt(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


class EventStore:
    """SQLite persistence for sensor events and executed actions."""

    def __init__(self, db_path: str | Path) -> None:
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sensor_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    sensor_id TEXT NOT NULL,
                    sensor_type TEXT NOT NULL,
                    value TEXT NOT NULL,
                    unit TEXT,
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_sensor_events_ts ON sensor_events(ts);
                CREATE INDEX IF NOT EXISTS idx_sensor_events_type ON sensor_events(sensor_type);

                CREATE TABLE IF NOT EXISTS executed_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    error TEXT,
                    payload_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_actions_ts ON executed_actions(ts);
                """
            )

    def record_sensor_event(self, reading: SensorReading) -> int:
        meta = json.dumps(reading.metadata, default=str)
        val = json.dumps(reading.value, default=str)
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO sensor_events (ts, sensor_id, sensor_type, value, unit, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    _serialize_dt(reading.ts),
                    reading.sensor_id,
                    reading.sensor_type,
                    val,
                    reading.unit,
                    meta,
                ),
            )
            return int(cur.lastrowid)

    def record_action(self, action: ExecutedAction) -> int:
        payload = json.dumps(action.payload, default=str)
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO executed_actions (ts, action_type, source, success, error, payload_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    _serialize_dt(action.ts),
                    action.action_type,
                    action.source,
                    1 if action.success else 0,
                    action.error,
                    payload,
                ),
            )
            return int(cur.lastrowid)

    def recent_sensor_events(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM sensor_events ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def recent_actions(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM executed_actions ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]
