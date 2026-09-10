from __future__ import annotations

import re
from dataclasses import dataclass

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")

_CLAUSE_END = re.compile(r"(?<=[,;:])\s+")


@dataclass(slots=True)
class StreamAssemblerConfig:
    min_chars: int = 24
    target_chars: int = 90
    max_chars: int = 180
    min_words: int = 4

    allow_clause_boundaries: bool = True


class SentenceStreamAssembler:
    def __init__(
        self,
        config: StreamAssemblerConfig,
    ) -> None:
        self.config = config

        self._buffer = ""

    @property
    def pending_text(self) -> str:
        return self._buffer

    def reset(self) -> None:
        self._buffer = ""

    def push(
        self,
        token_text: str,
    ) -> list[str]:
        if not token_text:
            return []

        self._buffer += token_text

        output: list[str] = []

        while True:
            segment = self._extract_segment()

            if segment is None:
                break

            output.append(segment)

        return output

    def flush(self) -> list[str]:
        remaining = self._buffer.strip()

        self._buffer = ""

        if not remaining:
            return []

        return [remaining]

    def _extract_segment(
        self,
    ) -> str | None:
        text = self._buffer.strip()

        if not text:
            return None

        if len(text) < self.config.min_chars:
            return None

        sentence_split = _SENTENCE_END.split(
            text,
            maxsplit=1,
        )

        if len(sentence_split) > 1:
            first = sentence_split[0].strip()

            if self._valid(first):
                consumed = len(sentence_split[0])

                self._buffer = text[consumed:].lstrip()

                return first

        if (
            self.config.allow_clause_boundaries
            and len(text) >= self.config.target_chars
        ):
            clause_split = _CLAUSE_END.split(
                text,
                maxsplit=1,
            )

            if len(clause_split) > 1:
                first = clause_split[0].strip()

                if self._valid(first):
                    consumed = len(clause_split[0])

                    self._buffer = text[consumed:].lstrip()

                    return first

        if len(text) >= self.config.max_chars:
            boundary = text.rfind(
                " ",
                0,
                self.config.max_chars,
            )

            if boundary <= 0:
                boundary = self.config.max_chars

            first = text[:boundary].strip()

            if self._valid(first):
                self._buffer = text[boundary:].lstrip()

                return first

        return None

    def _valid(
        self,
        text: str,
    ) -> bool:
        words = text.split()

        return (
            len(text) >= self.config.min_chars and len(words) >= self.config.min_words
        )
