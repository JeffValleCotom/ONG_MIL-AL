import json

from django.conf import settings
from openai import OpenAI, OpenAIError

from .base import (
    AIProvider,
    AIProviderError,
    AIProviderResult,
)


class OpenAIProvider(AIProvider):
    provider_name = "openai"

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise AIProviderError(
                "OPENAI_API_KEY no está configurada."
            )

        self.model = settings.AI_MODEL

        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.AI_TIMEOUT_SECONDS,
        )

    def generate_structured(
        self,
        *,
        system_prompt,
        user_prompt,
        schema_name,
        schema,
        max_output_tokens=1500,
    ):
        try:
            response = self.client.responses.create(
                model=self.model,
                reasoning={
                    "effort": (
                        settings.AI_REASONING_EFFORT
                    ),
                },
                input=[
                    {
                        "role": "developer",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                text={
                    "format": {
                        "type": "json_schema",
                        "name": schema_name,
                        "schema": schema,
                        "strict": True,
                    },
                },
                max_output_tokens=max_output_tokens,
                store=False,
            )
        except OpenAIError as exc:
            raise AIProviderError(
                "No fue posible completar "
                "la solicitud con OpenAI."
            ) from exc

        if response.status != "completed":
            raise AIProviderError(
                "La respuesta del proveedor "
                "no se completó correctamente."
            )

        if not response.output_text:
            raise AIProviderError(
                "El proveedor no devolvió contenido."
            )

        try:
            data = json.loads(
                response.output_text
            )
        except json.JSONDecodeError as exc:
            raise AIProviderError(
                "El proveedor devolvió una "
                "respuesta JSON inválida."
            ) from exc

        usage = None

        if response.usage is not None:
            if hasattr(
                response.usage,
                "model_dump",
            ):
                usage = response.usage.model_dump()

        return AIProviderResult(
            data=data,
            provider=self.provider_name,
            model=response.model,
            response_id=response.id,
            usage=usage,
        )
