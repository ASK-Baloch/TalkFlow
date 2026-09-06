from pydantic import (
    BaseModel,
    Field,
)


class SynthesisRequest(
    BaseModel
):
    text: str = Field(
        min_length=1,
        max_length=500,
    )

    voice_id: str = Field(
        min_length=1,
        max_length=100,
    )