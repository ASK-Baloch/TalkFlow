from app.realtime.tts.playback import (
    PCM_8K_MESSAGE_TYPE,
    AudioSocketPcmPlayer,
    encode_audiosocket_packet,
)


def test_packet_header():
    payload = b"\x00" * 320

    packet = (
        encode_audiosocket_packet(
            message_type=(
                PCM_8K_MESSAGE_TYPE
            ),
            payload=payload,
        )
    )

    assert packet[0] == 0x10

    assert packet[1] == 0x01
    assert packet[2] == 0x40

    assert packet[3:] == payload


def test_20ms_frame_size():
    player = (
        AudioSocketPcmPlayer(
            sample_rate=8000,
            sample_width_bytes=2,
            frame_ms=20,
        )
    )

    assert (
        player.samples_per_frame
        == 160
    )

    assert (
        player.bytes_per_frame
        == 320
    )