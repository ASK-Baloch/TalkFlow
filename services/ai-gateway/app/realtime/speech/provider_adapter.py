from __future__ import annotations

from abc import ABC


class SpeechProviderAdapter(ABC):
    provider_name = "generic"

    def adapt(
        self,
        text: str,
    ) -> str:
        return text


class GenericSpeechProviderAdapter(SpeechProviderAdapter):
    provider_name = "generic"


class ChatterboxSpeechProviderAdapter(SpeechProviderAdapter):
    provider_name = "chatterbox"

    def adapt(
        self,
        text: str,
    ) -> str:
        # Keep this deliberately conservative.
        #
        # Provider-specific rules may be added
        # here after real listening tests prove
        # that Chatterbox needs them.
        #
        # Do not put business logic here.

        return text


def create_provider_adapter(
    provider_name: str | None,
) -> SpeechProviderAdapter:
    normalized = (provider_name or "").strip().lower()

    if "chatterbox" in normalized:
        return ChatterboxSpeechProviderAdapter()

    return GenericSpeechProviderAdapter()
