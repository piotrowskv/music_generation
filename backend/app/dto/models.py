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
    token: str
