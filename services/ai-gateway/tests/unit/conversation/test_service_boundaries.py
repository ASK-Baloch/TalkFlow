from pathlib import Path


def test_tts_service_does_not_reference_llm():
    root = Path(__file__).resolve()

    while root.name != "ai-gateway" and root.parent != root:
        root = root.parent

    source = (
        (root / "app" / "realtime" / "tts" / "service.py")
        .read_text(encoding="utf-8")
        .lower()
    )

    forbidden = [
        "llmservice",
        "llm_service",
        "llmprovider",
        "llm_provider",
        "qwen",
        "vllm",
    ]

    for term in forbidden:
        assert term not in source


def test_llm_service_does_not_reference_tts():
    root = Path(__file__).resolve()

    while root.name != "ai-gateway" and root.parent != root:
        root = root.parent

    source = (
        (root / "app" / "realtime" / "llm" / "service.py")
        .read_text(encoding="utf-8")
        .lower()
    )

    forbidden = [
        "ttsservice",
        "tts_service",
        "ttsprovider",
        "tts_provider",
        "chatterbox",
        "playback",
    ]

    for term in forbidden:
        assert term not in source
