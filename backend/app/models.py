from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="building_admin")


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    address: Mapped[str] = mapped_column(String(255), default="")
    floors_count: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(16), default="online")

    floors: Mapped[list[Floor]] = relationship(back_populates="building")
    meters: Mapped[list[Meter]] = relationship(back_populates="building")


class Floor(Base):
    __tablename__ = "floors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"))
    floor_number: Mapped[int] = mapped_column(Integer, default=1)
    name: Mapped[str] = mapped_column(String(64), default="Floor 1")

    building: Mapped[Building] = relationship(back_populates="floors")
    zones: Mapped[list[Zone]] = relationship(back_populates="floor")


class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    floor_id: Mapped[int] = mapped_column(ForeignKey("floors.id"))
    name: Mapped[str] = mapped_column(String(64))
    type: Mapped[str] = mapped_column(String(32), default="office")

    floor: Mapped[Floor] = relationship(back_populates="zones")


class Meter(Base):
    __tablename__ = "meters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    type: Mapped[str] = mapped_column(String(32), default="three_phase")
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"))
    floor_id: Mapped[int | None] = mapped_column(ForeignKey("floors.id"), nullable=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("zones.id"), nullable=True)
    sampling_rate_hz: Mapped[int] = mapped_column(Integer, default=1)
    protocol: Mapped[str] = mapped_column(String(32), default="http")
    status: Mapped[str] = mapped_column(String(16), default="online")
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_power_kw: Mapped[float] = mapped_column(Float, default=0.0)

    building: Mapped[Building] = relationship(back_populates="meters")
    appliances: Mapped[list[Appliance]] = relationship(back_populates="meter")


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meter_id: Mapped[int] = mapped_column(ForeignKey("meters.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    power_w: Mapped[float] = mapped_column(Float, default=0.0)
    voltage_a: Mapped[float] = mapped_column(Float, default=220.0)
    current_a: Mapped[float] = mapped_column(Float, default=0.0)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meter_id: Mapped[int] = mapped_column(ForeignKey("meters.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    type: Mapped[str] = mapped_column(String(32))
    phase: Mapped[str] = mapped_column(String(8), default="a")
    delta_power_kw: Mapped[float] = mapped_column(Float, default=0.0)
    delta_reactive_kvar: Mapped[float] = mapped_column(Float, default=0.0)
    appliance_guess: Mapped[str] = mapped_column(String(64), default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)


class Appliance(Base):
    __tablename__ = "appliances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    type: Mapped[str] = mapped_column(String(64), index=True)
    meter_id: Mapped[int] = mapped_column(ForeignKey("meters.id"))
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("zones.id"), nullable=True)
    rated_power_kw: Mapped[float] = mapped_column(Float, default=1.0)

    meter: Mapped[Meter] = relationship(back_populates="appliances")


class DisaggregationCache(Base):
    __tablename__ = "disaggregation_cache"
    __table_args__ = (UniqueConstraint("meter_id", "period", name="uq_meter_period"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meter_id: Mapped[int] = mapped_column(ForeignKey("meters.id"), index=True)
    period: Mapped[str] = mapped_column(String(32))
    payload_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TaskStatus(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(String(255), default="")
    result_json: Mapped[str] = mapped_column(Text, default="")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    building_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    type: Mapped[str] = mapped_column(String(32), default="warning")
    title: Mapped[str] = mapped_column(String(128))
    message: Mapped[str] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
