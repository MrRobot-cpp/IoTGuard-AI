from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class AttackResult(Base):
    __tablename__ = "attack_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    payload_id: Mapped[str] = mapped_column(String, index=True)
    category: Mapped[str] = mapped_column(String)          # direct | indirect | multiturn
    payload: Mapped[str] = mapped_column(Text)
    llm_response: Mapped[str] = mapped_column(Text)
    success: Mapped[bool] = mapped_column(Boolean)          # did the attack succeed?
    blocked: Mapped[bool] = mapped_column(Boolean, default=False)  # was it blocked by mitigation?
    mitigation_active: Mapped[str] = mapped_column(String, default="none")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DeviceLog(Base):
    __tablename__ = "device_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[str] = mapped_column(String, index=True)
    action: Mapped[str] = mapped_column(String)
    triggered_by: Mapped[str] = mapped_column(String)       # user | attack | sensor
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MitigationScore(Base):
    __tablename__ = "mitigation_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    mitigation: Mapped[str] = mapped_column(String)
    attack_category: Mapped[str] = mapped_column(String)
    total_attacks: Mapped[int] = mapped_column(Integer, default=0)
    blocked: Mapped[int] = mapped_column(Integer, default=0)
    success_rate: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
