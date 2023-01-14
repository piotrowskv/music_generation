from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel


@dataclass(frozen=True)
class EndpointError(BaseModel):
    status_code: int
    detail: str
    headers: dict[str, Any] | None
