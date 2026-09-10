from app.realtime.response.stream_assembler import (
    SentenceStreamAssembler,
    StreamAssemblerConfig,
)


def make_assembler():
    return SentenceStreamAssembler(
        StreamAssemblerConfig(
            min_chars=10,
            target_chars=40,
            max_chars=100,
            min_words=2,
            allow_clause_boundaries=True,
        )
    )


def test_sentence_is_emitted():
    assembler = make_assembler()

    output = []

    output += assembler.push("Medicare Part A generally ")

    output += assembler.push("covers hospital care. ")

    output += assembler.flush()

    assert output == [("Medicare Part A generally covers hospital care.")]


def test_partial_sentence_is_not_emitted_too_early():
    assembler = make_assembler()

    output = assembler.push("Medicare Part")

    assert output == []


def test_final_buffer_flushes():
    assembler = make_assembler()

    assembler.push("This is the final response")

    output = assembler.flush()

    assert output == ["This is the final response"]


def test_reset_drops_pending_text():
    assembler = make_assembler()

    assembler.push("This should never be spoken")

    assembler.reset()

    assert assembler.pending_text == ""
