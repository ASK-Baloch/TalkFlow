from __future__ import annotations

import hashlib
import json
import wave
from pathlib import Path

import numpy as np
import soxr


ROOT = Path(__file__).resolve().parents[2]

ASSET_DIR = ROOT / "assets" / "tts" / "talkflow-chatterbox-v1"

TARGET_SAMPLE_RATE = 8000


def read_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        sample_rate = wav.getframerate()

        frames = wav.readframes(
            wav.getnframes()
        )

    if sample_width != 2:
        raise ValueError(
            f"{path}: expected PCM16 WAV, got "
            f"{sample_width * 8}-bit"
        )

    audio = np.frombuffer(
        frames,
        dtype="<i2",
    ).astype(np.float32)

    audio /= 32768.0

    if channels > 1:
        audio = audio.reshape(
            -1,
            channels,
        ).mean(axis=1)

    return audio, sample_rate


def to_pcm16(audio: np.ndarray) -> bytes:
    audio = np.asarray(
        audio,
        dtype=np.float32,
    )

    audio = np.nan_to_num(
        audio,
        nan=0.0,
        posinf=1.0,
        neginf=-1.0,
    )

    peak = (
        float(np.max(np.abs(audio)))
        if audio.size
        else 0.0
    )

    if peak > 0.98:
        audio *= 0.98 / peak

    audio = np.clip(
        audio,
        -1.0,
        1.0,
    )

    return np.round(
        audio * 32767.0
    ).astype("<i2").tobytes()


def main() -> None:
    manifest = {
        "schema_version": 1,
        "asset_version": "talkflow-chatterbox-v1",
        "generator": "chatterbox-turbo",
        "sample_rate": 8000,
        "channels": 1,
        "sample_width_bytes": 2,
        "encoding": "signed_pcm16_little_endian",
        "responses": {},
    }

    wav_files = sorted(
        ASSET_DIR.glob("*.wav")
    )

    if not wav_files:
        raise RuntimeError(
            f"No WAV files found in {ASSET_DIR}"
        )

    for wav_path in wav_files:
        response_id = wav_path.stem

        audio, source_rate = read_wav(
            wav_path
        )

        resampled = soxr.resample(
            audio,
            source_rate,
            TARGET_SAMPLE_RATE,
            quality="HQ",
        )

        pcm = to_pcm16(resampled)

        pcm_path = (
            ASSET_DIR
            / f"{response_id}.pcm"
        )

        pcm_path.write_bytes(pcm)

        sha256 = hashlib.sha256(
            pcm
        ).hexdigest()

        sample_count = len(pcm) // 2

        duration_ms = (
            sample_count
            / TARGET_SAMPLE_RATE
            * 1000
        )

        manifest["responses"][
            response_id
        ] = {
            "file": pcm_path.name,
            "source_file": wav_path.name,
            "source_sample_rate": source_rate,
            "bytes": len(pcm),
            "sample_count": sample_count,
            "duration_ms": round(
                duration_ms,
                3,
            ),
            "sha256": sha256,
        }

        print(
            f"{response_id}: "
            f"{source_rate} Hz -> 8000 Hz, "
            f"{duration_ms:.1f} ms"
        )

    manifest_path = (
        ASSET_DIR / "manifest.json"
    )

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(
        f"Converted {len(wav_files)} assets."
    )
    print(
        f"Manifest: {manifest_path}"
    )


if __name__ == "__main__":
    main()
