from app.realtime.recording.publisher import RecordingRequestPublisher


class RecordingCoordinator:
    def __init__(self, publisher: RecordingRequestPublisher):
        self.publisher = publisher

    async def call_ended(self, call_id: str) -> None:
        """
        Called when an AudioSocket session ends.
        Publishes a metadata event so that the recording worker can download the recording.
        """
        await self.publisher.publish_call_ended(call_id=call_id)
