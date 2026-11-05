from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class AIProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class AIProviderResult:
    data: dict[str, Any]
    provider: str
    model: str
    response_id: str | None = None
    usage: dict[str, Any] | None = None


class AIProvider(ABC):
    @abstractmethod
    def generate_structured(
        self,
        *,
        system_prompt,
        user_prompt,
        schema_name,
        schema,
        max_output_tokens=1500,
    ):
        raise NotImplementedError
