from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

TONES = ("contemporary", "author")
MODES = ("narrate", "translate")


@dataclass
class Chapter:
    index: int
    title: str
    paragraphs: list[str] = field(default_factory=list)


@dataclass
class Book:
    title: str
    author: str
    chapters: list[Chapter] = field(default_factory=list)


@dataclass
class BookConfig:
    slug: str
    title: str
    author: str = ""
    source_lang: str = "en"  # en | ta
    mode: str = "narrate"  # narrate | translate
    tone: str | None = None  # contemporary | author (Tamil output only)
    rights: str = "owned"  # owned | public-domain | licensed
    voices: dict[str, str] = field(default_factory=dict)

    @property
    def target_lang(self) -> str:
        if self.mode == "translate":
            return "ta"
        return self.source_lang

    def save(self, folder: Path) -> None:
        (folder / "book.yaml").write_text(
            yaml.safe_dump(self.__dict__, allow_unicode=True, sort_keys=False)
        )

    @classmethod
    def load(cls, folder: Path) -> "BookConfig":
        return cls(**yaml.safe_load((folder / "book.yaml").read_text()))
