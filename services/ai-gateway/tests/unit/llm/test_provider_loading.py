from app.realtime.providers.llm_dummy import (
    DummyLLMProvider,
)
from app.realtime.providers.loader import (
    create_provider,
)


class Settings:
    llm_dummy_response = "Test response."


def test_load_dummy_llm_provider():
    provider = create_provider(
        ("app.realtime.providers.llm_dummy:DummyLLMProvider"),
        settings=Settings(),
    )

    assert isinstance(
        provider,
        DummyLLMProvider,
    )
