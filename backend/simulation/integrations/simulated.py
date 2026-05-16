from __future__ import annotations

import logging
import random
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from ..models import utc_now

log = logging.getLogger(__name__)


@dataclass
class SimulatedEmail:
    message_id: str
    to_addr: str
    subject: str
    body: str
    sent_at: datetime


class EmailSimulator:
    """In-memory fake SMTP-style sends."""

    def __init__(self) -> None:
        self._outbox: list[SimulatedEmail] = []

    def send(self, to_addr: str, subject: str, body: str) -> SimulatedEmail:
        msg = SimulatedEmail(
            message_id=str(uuid.uuid4()),
            to_addr=to_addr,
            subject=subject,
            body=body,
            sent_at=utc_now(),
        )
        self._outbox.append(msg)
        log.info("simulated email to=%s subject=%s", to_addr, subject)
        return msg

    def list_outbox(self, limit: int = 20) -> list[SimulatedEmail]:
        return list(reversed(self._outbox[-limit:]))


@dataclass
class CalendarEvent:
    event_id: str
    title: str
    start: datetime
    end: datetime
    location: str


class CalendarSimulator:
    """Simple in-memory calendar."""

    def __init__(self) -> None:
        self._events: dict[str, CalendarEvent] = {}

    def add_event(self, title: str, start: datetime, duration_minutes: int = 60, location: str = "") -> CalendarEvent:
        eid = str(uuid.uuid4())
        ev = CalendarEvent(
            event_id=eid,
            title=title,
            start=start,
            end=start + timedelta(minutes=duration_minutes),
            location=location,
        )
        self._events[eid] = ev
        return ev

    def upcoming(self, within_hours: int = 24) -> list[CalendarEvent]:
        now = utc_now()
        horizon = now + timedelta(hours=within_hours)
        out = [e for e in self._events.values() if now <= e.start <= horizon]
        return sorted(out, key=lambda e: e.start)

    def seed_demo(self) -> None:
        now = utc_now().replace(minute=0, second=0, microsecond=0)
        self.add_event("Maintenance window", now + timedelta(hours=2), 30, "Server room")
        self.add_event("Team sync", now + timedelta(hours=6), 45, "Video call")


class WebFetchSimulator:
    """Returns canned content by default; optional real HTTP GET."""

    def __init__(self, *, allow_network: bool = False, timeout_sec: float = 5.0) -> None:
        self._allow_network = allow_network
        self._timeout = timeout_sec

    def fetch(self, url: str) -> dict[str, Any]:
        if not self._allow_network:
            return {
                "url": url,
                "simulated": True,
                "status": 200,
                "content_type": "text/plain",
                "text": f"[simulated body for {url}]\nLorem ipsum connected home demo.",
            }
        try:
            req = Request(url, headers={"User-Agent": "SensorSimulation/1.0"})
            with urlopen(req, timeout=self._timeout) as resp:
                raw = resp.read()[:50_000]
                text = raw.decode("utf-8", errors="replace")
                return {
                    "url": url,
                    "simulated": False,
                    "status": getattr(resp, "status", 200),
                    "content_type": resp.headers.get("Content-Type", ""),
                    "text": text,
                }
        except URLError as e:
            log.warning("web fetch failed: %s", e)
            return {"url": url, "simulated": False, "error": str(e), "text": ""}
