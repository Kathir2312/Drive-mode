import re
from pathlib import Path

from ..models import Book, Chapter
from .clean import clean_paragraphs

_CHAPTER = re.compile(r"^\s*(chapter|அத்தியாயம்)\b.*$", re.IGNORECASE | re.MULTILINE)


def read_txt(path: Path) -> Book:
    text = path.read_text(encoding="utf-8")
    marks = list(_CHAPTER.finditer(text))
    if not marks:
        parts = [(path.stem, text)]
    else:
        parts = [
            (m.group().strip(), text[m.end() : marks[i + 1].start() if i + 1 < len(marks) else len(text)])
            for i, m in enumerate(marks)
        ]
    chapters = [
        Chapter(i + 1, title, clean_paragraphs(re.split(r"\n\s*\n", body)))
        for i, (title, body) in enumerate(parts)
    ]
    return Book(title=path.stem, author="", chapters=[c for c in chapters if c.paragraphs])
