from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import wave
from pathlib import Path

import numpy as np
import soxr
from kokoro_onnx import Kokoro

try:
    from chatterbox.tts_turbo import ChatterboxTurboTTS
except ImportError:
    ChatterboxTurboTTS = None


SOURCE_SAMPLE_RATE_FALLBACK = 24000
TARGET_SAMPLE_RATE = 8000

CHANNELS = 1
SAMPLE_WIDTH_BYTES = 2


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


ROOT = repository_root()

sys.path.insert(
    0,
    str(
        ROOT
        / "services"
        / "ai-gateway"
    ),
)

from app.realtime.tts.catalog import RESPONSES


def float32_to_pcm16(
    audio: np.ndarray,
) -> bytes:
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

    peak = float(
        np.max(np.abs(audio))
    ) if audio.size else 0.0

    # Prevent clipping without unnecessarily
    # normalizing already-good audio.
    if peak > 0.98:
        audio = audio * (
            0.98 / peak
        )

    audio = np.clip(
        audio,
        -1.0,
        1.0,
    )

    pcm = np.round(
        audio * 32767.0
    ).astype(
        "<i2"
    )

    return pcm.tobytes()


def write_preview_wav(
    path: Path,
    pcm: bytes,
    *,
    sample_rate: int,
) -> None:
    with wave.open(
        str(path),
        "wb",
    ) as wav:
        wav.setnchannels(
            CHANNELS
        )

        wav.setsampwidth(
            SAMPLE_WIDTH_BYTES
        )

        wav.setframerate(
            sample_rate
        )

        wav.writeframes(
            pcm
        )


def generate(
    *,
    provider: str,
    model_path: Path,
    voices_path: Path,
    output_dir: Path,
    voice: str,
    speed: float,
    language: str,
    write_wav: bool,
    chatterbox_device: str = "cuda",
    voice_reference: Path | None = None,
) -> None:
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    model = None
    if provider == "kokoro":
        print("Loading Kokoro...")
        t0 = time.perf_counter()
        model = Kokoro(
            str(model_path),
            str(voices_path),
        )
        print(f"Kokoro loaded in {time.perf_counter() - t0:.2f}s")
    elif provider == "chatterbox":
        if ChatterboxTurboTTS is None:
            raise RuntimeError("chatterbox-tts is not installed. Please install it to use Chatterbox Turbo.")
        if not voice_reference or not voice_reference.exists():
            raise FileNotFoundError(f"Chatterbox voice reference audio not found: {voice_reference}")
        print("Loading Chatterbox Turbo...")
        t0 = time.perf_counter()
        model = ChatterboxTurboTTS.from_pretrained(device=chatterbox_device)
        print(f"Chatterbox Turbo loaded in {time.perf_counter() - t0:.2f}s")
    else:
        raise ValueError(f"Unknown TTS provider: {provider}")

    manifest: dict = {
        "schema_version": 1,
        "asset_version": (
            output_dir.name
        ),
        "voice": voice,
        "speed": speed,
        "language": language,
        "sample_rate": (
            TARGET_SAMPLE_RATE
        ),
        "channels": CHANNELS,
        "sample_width_bytes": (
            SAMPLE_WIDTH_BYTES
        ),
        "encoding": (
            "signed_pcm16_little_endian"
        ),
        "responses": {},
    }

    for response_id, definition in RESPONSES.items():
        print(
            f"Generating {response_id.value}..."
        )

        t_gen_start = time.perf_counter()

        if provider == "kokoro":
            samples, sample_rate = model.create(
                definition.text,
                voice=voice,
                speed=speed,
                lang=language,
            )
        else:
            samples = model.generate(
                definition.text,
                audio_prompt_path=str(voice_reference),
            )
            sample_rate = getattr(model, "sr", SOURCE_SAMPLE_RATE_FALLBACK)

        t_gen_end = time.perf_counter()
        gen_duration_s = t_gen_end - t_gen_start

        source = np.asarray(
            samples,
            dtype=np.float32,
        ).reshape(-1)

        if not sample_rate:
            sample_rate = (
                SOURCE_SAMPLE_RATE_FALLBACK
            )

        resampled = soxr.resample(
            source,
            int(sample_rate),
            TARGET_SAMPLE_RATE,
            quality="HQ",
        )

        pcm = float32_to_pcm16(
            resampled
        )

        pcm_path = (
            output_dir
            / f"{response_id.value}.pcm"
        )

        pcm_path.write_bytes(
            pcm
        )

        if write_wav:
            write_preview_wav(
                output_dir
                / f"{response_id.value}.wav",
                pcm,
                sample_rate=(
                    TARGET_SAMPLE_RATE
                ),
            )

        sha256 = hashlib.sha256(
            pcm
        ).hexdigest()

        sample_count = (
            len(pcm)
            // SAMPLE_WIDTH_BYTES
        )

        duration_ms = (
            sample_count
            / TARGET_SAMPLE_RATE
            * 1000.0
        )

        audio_duration_s = duration_ms / 1000.0
        rtf = gen_duration_s / audio_duration_s if audio_duration_s > 0 else 0.0

        print(
            f"  Generated in {gen_duration_s:.3f}s, Audio: {audio_duration_s:.3f}s, RTF: {rtf:.3f}"
        )

        manifest[
            "responses"
        ][response_id.value] = {
            "text": definition.text,
            "file": pcm_path.name,
            "sha256": sha256,
            "bytes": len(pcm),
            "sample_count": (
                sample_count
            ),
            "duration_ms": round(
                duration_ms,
                3,
            ),
        }

    manifest_path = (
        output_dir
        / "manifest.json"
    )

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        f"Generated {len(RESPONSES)} "
        f"responses in {output_dir}"
    )

    print(
        f"Manifest: {manifest_path}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--provider",
        choices=["kokoro", "chatterbox"],
        default="kokoro",
    )

    parser.add_argument(
        "--model",
        default=(
            "tools/tts-assets/"
            "models/kokoro-v1.0.onnx"
        ),
    )

    parser.add_argument(
        "--voices",
        default=(
            "tools/tts-assets/"
            "models/voices-v1.0.bin"
        ),
    )

    parser.add_argument(
        "--chatterbox-device",
        default="cuda",
    )

    parser.add_argument(
        "--voice-reference",
        default="assets/voices/talkflow/talkflow_reference.wav",
    )

    parser.add_argument(
        "--output",
        default=(
            "assets/tts/talkflow-v1"
        ),
    )

    parser.add_argument(
        "--voice",
        default="af_heart",
    )

    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
    )

    parser.add_argument(
        "--language",
        default="en-us",
    )

    parser.add_argument(
        "--write-wav",
        action="store_true",
    )

    args = parser.parse_args()

    generate(
        provider=args.provider,
        model_path=(
            ROOT / args.model
        ).resolve(),
        voices_path=(
            ROOT / args.voices
        ).resolve(),
        output_dir=(
            ROOT / args.output
        ).resolve(),
        voice=args.voice,
        speed=args.speed,
        language=args.language,
        write_wav=(
            args.write_wav
        ),
        chatterbox_device=args.chatterbox_device,
        voice_reference=(ROOT / args.voice_reference).resolve() if args.voice_reference else None,
    )


if __name__ == "__main__":
    main()