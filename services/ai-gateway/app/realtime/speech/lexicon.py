from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class LexiconEntry:
    source: str
    target: str
    case_sensitive: bool = False


class PronunciationLexicon:
    def __init__(
        self,
        entries: list[LexiconEntry],
    ) -> None:
        self.entries = entries

    @classmethod
    def from_file(
        cls,
        path: str,
    ) -> PronunciationLexicon:
        lexicon_path = Path(path)

        if not lexicon_path.exists():
            raise FileNotFoundError(f"Pronunciation lexicon not found: {path}")

        data = json.loads(lexicon_path.read_text(encoding="utf-8"))

        entries = [
            LexiconEntry(
                source=item["source"],
                target=item["target"],
                case_sensitive=(
                    item.get(
                        "case_sensitive",
                        False,
                    )
                ),
            )
            for item in data.get("replacements", [])
        ]

        return cls(entries)

    def apply(
        self,
        text: str,
    ) -> tuple[str, list[str]]:
        result = text
        rules: list[str] = []

        for entry in self.entries:
            flags = 0 if entry.case_sensitive else re.IGNORECASE

            pattern = re.compile(
                re.escape(entry.source),
                flags,
            )

            updated = pattern.sub(
                entry.target,
                result,
            )

            if updated != result:
                rules.append(f"lexicon:{entry.source}")

                result = updated

        return result, rules
