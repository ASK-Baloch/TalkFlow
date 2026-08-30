from app.realtime.vad.detector import (
    VadDetector,
    VadDetectorConfig,
)
from app.realtime.vad.types import (
    VadEventType,
)


def create_detector():
    return VadDetector(
        VadDetectorConfig(
            sample_rate=8000,
            chunk_samples=256,
            threshold=0.50,
            neg_threshold=0.35,
            min_speech_ms=96,
            min_silence_ms=256,
            max_speech_seconds=30,
        )
    )


def test_speech_start_requires_sustained_speech():
    detector = create_detector()

    events = []

    # Three 32ms speech chunks = 96ms.
    for probability in (
        0.8,
        0.9,
        0.85,
    ):
        events.extend(detector.process_probability(probability))

    assert len(events) == 1

    assert events[0].event_type == VadEventType.SPEECH_START


def test_short_noise_does_not_trigger():
    detector = create_detector()

    events = []

    events.extend(detector.process_probability(0.9))

    events.extend(detector.process_probability(0.1))

    assert events == []


def test_speech_end_after_sustained_silence():
    detector = create_detector()

    events = []

    for _ in range(3):
        events.extend(detector.process_probability(0.9))

    assert any(event.event_type == VadEventType.SPEECH_START for event in events)

    events.clear()

    # 8 × 32ms = 256ms.
    for _ in range(8):
        events.extend(detector.process_probability(0.05))

    assert any(event.event_type == VadEventType.SPEECH_END for event in events)


def test_short_pause_does_not_end_speech():
    detector = create_detector()

    for _ in range(3):
        detector.process_probability(0.9)

    # Only 128ms silence.
    events = []

    for _ in range(4):
        events.extend(detector.process_probability(0.05))

    assert not any(event.event_type == VadEventType.SPEECH_END for event in events)

    # Speech resumes.
    events = detector.process_probability(0.9)

    assert events == []
