import asyncio

from app.realtime.tts.types import (
    PlaybackRequest,
    ResponseId,
)


class DummyWriter:
    pass


def test_queue_can_be_flushed():
    async def run():
        queue = asyncio.Queue(maxsize=8)

        await queue.put(
            PlaybackRequest(
                connection_id="call-1",
                generation=0,
                response_id=(ResponseId.ASK_NAME),
            )
        )

        await queue.put(
            PlaybackRequest(
                connection_id="call-1",
                generation=0,
                response_id=(ResponseId.ASK_AGE),
            )
        )

        count = 0

        while True:
            try:
                queue.get_nowait()

            except asyncio.QueueEmpty:
                break

            else:
                queue.task_done()
                count += 1

        assert count == 2

        assert queue.empty()

    asyncio.run(run())
