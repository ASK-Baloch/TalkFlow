import asyncio

import pytest

from app.core.config import Settings
from app.realtime.providers.tts_dummy import DummyTTSProvider
from app.realtime.tts.barge_in import BargeInConfig, BargeInController
from app.realtime.tts.metrics import tts_metrics
from app.realtime.tts.planner import PlannedResponse, TTSRoute
from app.realtime.tts.service import TTSService


class FakeWriter:
    def __init__(self):
        self.writes = []

    def write(self, data: bytes):
        self.writes.append(data)

    async def drain(self):
        return None


@pytest.mark.asyncio
async def test_barge_in_stops_playback():
    # Configure dummy provider with 250 frames (5 seconds)
    settings = Settings(tts_dummy_frames=250)
    provider = DummyTTSProvider(
        sample_rate=8000,
        frames=settings.tts_dummy_frames,
        frame_ms=20,
    )

    tts_service = TTSService(
        pregenerated_provider=provider,
        dynamic_provider=provider,
        sample_rate=8000,
        sample_width_bytes=2,
        frame_ms=20,
        queue_size=10,
        interrupt_enabled=True,
        flush_queue_on_interrupt=True,
        drop_stale_audio=True,
        barge_in_log_events=False,
    )

    barge_in_controller = BargeInController(
        tts_service=tts_service,
        config=BargeInConfig(enabled=True, grace_ms=0, log_events=False),
    )

    writer = FakeWriter()
    connection_id = "test-barge-in-1"

    await tts_service.attach_connection(
        connection_id=connection_id,
        writer=writer,
    )

    # Enqueue a dummy response

    # Store initial metrics
    initial_interruptions = tts_metrics.interruptions_total
    initial_interrupted_playbacks = tts_metrics.interrupted_playbacks_total

    planned = PlannedResponse(
        route=TTSRoute.DYNAMIC, display_text="dummy", tts_text="dummy"
    )
    await tts_service.enqueue(connection_id=connection_id, planned=planned)

    # Wait 300 ms to let playback begin writing frames
    await asyncio.sleep(0.3)

    assert tts_metrics.active_playbacks == 1

    frames_before_interrupt = len(writer.writes)
    assert frames_before_interrupt > 0

    # Emit VAD SPEECH_START -> Barge-in immediately cancels playback
    await barge_in_controller.on_speech_start(connection_id=connection_id)

    # Wait another 200 ms
    await asyncio.sleep(0.2)

    frames_after_interrupt = len(writer.writes)

    # Verify playback was canceled correctly (didn't reach the full 250 frames)
    assert frames_after_interrupt < 250
    # Frames shouldn't continue accumulating significantly after interruption
    assert frames_after_interrupt <= frames_before_interrupt + 5

    # Verify metrics
    assert tts_metrics.active_playbacks == 0
    assert tts_metrics.interruptions_total == initial_interruptions + 1
    assert tts_metrics.interrupted_playbacks_total == initial_interrupted_playbacks + 1

    # Clean up
    await tts_service.detach_connection(connection_id)
