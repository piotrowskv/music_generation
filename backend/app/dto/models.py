import datetime
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
class TrainingSession(BaseModel):
    session_id: str
    model: ModelVariant
    created_at: datetime.datetime
    training_file_names: list[str]


@dataclass(frozen=True)
class ChartPoint(BaseModel):
    x: float
    y: float


@dataclass(frozen=True)
class TrainingProgress(BaseModel):
    finished: bool
    x_label: str
    y_label: str
    legends: list[str]
    chart_series_points: list[list[ChartPoint]]


@dataclass(frozen=True)
class TrainingSessionSummary(BaseModel):
    session_id: str
    model_name: str
    created_at: datetime.datetime
    file_count: int
    training_completed: bool


@dataclass(frozen=True)
class AllTrainingSessions(BaseModel):
    sessions: list[TrainingSessionSummary]
