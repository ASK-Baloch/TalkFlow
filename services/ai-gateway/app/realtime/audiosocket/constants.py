from enum import IntEnum


class AudioSocketMessageType(IntEnum):
    TERMINATE = 0x00
    UUID = 0x01
    DTMF = 0x03

    PCM_8K = 0x10
    PCM_12K = 0x11
    PCM_16K = 0x12
    PCM_24K = 0x13
    PCM_32K = 0x14
    PCM_44K = 0x15
    PCM_48K = 0x16
    PCM_96K = 0x17
    PCM_192K = 0x18

    ERROR = 0xFF


HEADER_SIZE = 3
MAX_PAYLOAD_SIZE = 65535