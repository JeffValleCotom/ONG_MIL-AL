from django.conf import settings

from .base import AIProviderError
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider


def get_ai_provider():
    provider = settings.AI_PROVIDER

    if provider == "openai":
        return OpenAIProvider()

    if provider == "ollama":
        return OllamaProvider()

    raise AIProviderError(
        (
            "Proveedor de inteligencia "
            f"artificial no soportado: {provider}"
        )
    )
