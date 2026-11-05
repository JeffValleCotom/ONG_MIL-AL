import json
from urllib import error
from urllib import request

from django.conf import settings

from .base import (
    AIProvider,
    AIProviderError,
    AIProviderResult,
)


class OllamaProvider(AIProvider):
    provider_name = "ollama"

    def __init__(self):
        self.model = settings.AI_MODEL
        self.base_url = settings.OLLAMA_BASE_URL

    def generate_structured(
        self,
        *,
        system_prompt,
        user_prompt,
        schema_name,
        schema,
        max_output_tokens=1500,
    ):
        del schema_name

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "stream": False,
            "format": schema,
            "options": {
                "temperature": 0,
                "num_predict": max_output_tokens,
            },
        }

        body = json.dumps(
            payload
        ).encode("utf-8")

        http_request = request.Request(
            (
                f"{self.base_url}"
                "/api/chat"
            ),
            data=body,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(
                http_request,
                timeout=settings.AI_TIMEOUT_SECONDS,
            ) as response:
                response_body = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )
        except (
            error.URLError,
            TimeoutError,
            json.JSONDecodeError,
        ) as exc:
            raise AIProviderError(
                "No fue posible completar "
                "la solicitud con Ollama."
            ) from exc

        content = (
            response_body
            .get("message", {})
            .get("content")
        )

        if not content:
            raise AIProviderError(
                "Ollama no devolvió contenido."
            )

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise AIProviderError(
                "Ollama devolvió una "
                "respuesta JSON inválida."
            ) from exc

        usage = {
            "input_tokens": (
                response_body.get(
                    "prompt_eval_count"
                )
            ),
            "output_tokens": (
                response_body.get(
                    "eval_count"
                )
            ),
        }

        return AIProviderResult(
            data=data,
            provider=self.provider_name,
            model=self.model,
            usage=usage,
        )
