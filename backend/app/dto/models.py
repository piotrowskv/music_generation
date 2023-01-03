from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class ModelVariant(BaseModel):
    id: str
    name: str
    description: str


@dataclass(frozen=True)
class ModelVariants(BaseModel):
    variants: list[ModelVariant]


@dataclass(frozen=True)
class TrainingSessionCreated(BaseModel):
    session_id: str


@dataclass(frozen=True)
class ChartPoint(BaseModel):
    x: float
    y: float


@dataclass(frozen=True)
class ChartSeries(BaseModel):
    legend: str
    points: list[ChartPoint]


@dataclass(frozen=True)
class TrainingProgress(BaseModel):
    finished: bool
    x_label: str
    y_label: str
    chart_series: list[ChartSeries]
