from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: T | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    building_ids: list[int] = []

    model_config = {"from_attributes": True}


class LoginData(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    user: UserOut


class BuildingCreate(BaseModel):
    name: str
    address: str = ""
    floors_count: int = 1


class BuildingOut(BaseModel):
    id: int
    name: str
    address: str
    floors_count: int
    meters_count: int = 0
    total_power_kw: float = 0.0
    status: str

    model_config = {"from_attributes": True}


class FloorOut(BaseModel):
    id: int
    building_id: int
    floor_number: int
    name: str
    zones_count: int = 0

    model_config = {"from_attributes": True}


class ZoneCreate(BaseModel):
    name: str
    type: str = "office"


class ZoneOut(BaseModel):
    id: int
    floor_id: int
    name: str
    type: str

    model_config = {"from_attributes": True}


class MeterLocation(BaseModel):
    building_id: int
    floor_id: int | None = None
    zone_id: int | None = None


class PhaseData(BaseModel):
    voltage: float = 220.0
    current: float = 0.0
    power_kw: float = 0.0


class MeterCurrent(BaseModel):
    phase_a: PhaseData = Field(default_factory=PhaseData)
    phase_b: PhaseData = Field(default_factory=PhaseData)
    phase_c: PhaseData = Field(default_factory=PhaseData)
    total_power_kw: float = 0.0


class MeterCreate(BaseModel):
    name: str
    type: str = "three_phase"
    location: MeterLocation
    sampling_rate_hz: int = 1
    protocol: str = "http"
    id: int | None = None


class MeterOut(BaseModel):
    id: int
    name: str
    type: str
    location: MeterLocation
    sampling_rate_hz: int
    protocol: str
    status: str
    last_seen: datetime | None = None
    current: MeterCurrent | None = None


class MeasurementSample(BaseModel):
    timestamp: datetime
    phase_a: PhaseData = Field(default_factory=PhaseData)
    phase_b: PhaseData = Field(default_factory=PhaseData)
    phase_c: PhaseData = Field(default_factory=PhaseData)
    power_w: float | None = None


class MeasurementUpload(BaseModel):
    meter_id: int
    edge_node_id: str | None = None
    samples: list[MeasurementSample]


class EventOut(BaseModel):
    id: int
    meter_id: int
    timestamp: datetime
    type: str
    phase: str
    delta_power_kw: float
    delta_reactive_kvar: float
    appliance_guess: str
    confidence: float

    model_config = {"from_attributes": True}


class ApplianceCreate(BaseModel):
    name: str
    type: str
    meter_id: int
    zone_id: int | None = None
    rated_power_kw: float = 1.0


class ApplianceOut(BaseModel):
    id: int
    name: str
    type: str
    meter_id: int
    zone_id: int | None
    rated_power_kw: float

    model_config = {"from_attributes": True}


class DisaggregationRun(BaseModel):
    meter_id: int
    start: datetime
    end: datetime


class SeriesPoint(BaseModel):
    timestamp: datetime
    power_kw: float


class ApplianceEnergy(BaseModel):
    appliance_id: int
    type: str
    name: str
    energy_kwh: float
    percentage: float
    runtime_hours: float
    series: list[SeriesPoint] = []
    power_w: float = 0.0
    state: bool = False
    confidence: float = 0.9


class DisaggregationResult(BaseModel):
    meter_id: int
    period: str
    total_energy_kwh: float
    appliances: list[ApplianceEnergy]
    mains_series: list[SeriesPoint] = []
