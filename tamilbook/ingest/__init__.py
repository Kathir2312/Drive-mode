from pathlib import Path

from ..models import Book
from .epub import read_epub
from .txt import read_txt


def read_book(path: Path) -> Book:
    suffix = path.suffix.lower()
    if suffix == ".epub":
        return read_epub(path)
    if suffix in (".txt", ".md"):
        return read_txt(path)
    raise ValueError(f"Unsupported format {suffix!r}; MOBI/PDF/DOCX arrive in M1")
