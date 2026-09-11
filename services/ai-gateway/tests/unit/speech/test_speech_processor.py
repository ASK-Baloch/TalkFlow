from app.realtime.response.speech import (
    ResponseSpeechProcessor,
)
from app.realtime.speech.types import (
    NormalizedSpeech,
)
from app.realtime.tts.planner import (
    PlannedResponse,
    TTSRoute,
)


class FakeSpeechService:
    def normalize(
        self,
        text,
        *,
        context=None,
    ):
        del context

        return NormalizedSpeech(
            display_text=text,
            tts_text=("Your zip code is seven five zero zero one."),
            changed=True,
            rules_applied=["zip_code"],
        )


def test_dynamic_text_normalized():
    processor = ResponseSpeechProcessor(speech_service=(FakeSpeechService()))

    planned = PlannedResponse(
        route=TTSRoute.DYNAMIC,
        display_text=("Your ZIP code is 75001."),
        tts_text=("Your ZIP code is 75001."),
    )

    result = processor.process(planned)

    assert result.display_text == ("Your ZIP code is 75001.")

    assert result.tts_text == ("Your zip code is seven five zero zero one.")


def test_pregenerated_bypasses_normalizer():
    processor = ResponseSpeechProcessor(speech_service=(FakeSpeechService()))

    planned = PlannedResponse(
        route=(TTSRoute.PREGENERATED),
        response_id="ask_zip",
    )

    result = processor.process(planned)

    assert result is planned
