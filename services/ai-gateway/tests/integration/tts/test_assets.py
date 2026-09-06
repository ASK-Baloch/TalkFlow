import hashlib
import json
from pathlib import Path


def test_generated_assets_are_valid():
    repo_root = Path(__file__).resolve().parents[5]
    root = repo_root / "assets/tts/talkflow-v1"

    manifest = json.loads(
        (
            root / "manifest.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    assert (
        manifest["sample_rate"]
        == 8000
    )

    assert (
        manifest["channels"]
        == 1
    )

    assert (
        manifest[
            "sample_width_bytes"
        ]
        == 2
    )

    assert manifest[
        "responses"
    ]

    for (
        response_id,
        metadata,
    ) in manifest[
        "responses"
    ].items():
        path = (
            root
            / metadata["file"]
        )

        assert path.exists(), (
            response_id
        )

        pcm = path.read_bytes()

        assert len(pcm) > 0

        assert len(pcm) % 2 == 0

        digest = hashlib.sha256(
            pcm
        ).hexdigest()

        assert (
            digest
            == metadata["sha256"]
        )