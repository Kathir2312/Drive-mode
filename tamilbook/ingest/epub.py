from pathlib import Path

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub

from ..models import Book, Chapter
from .clean import clean_paragraphs


def read_epub(path: Path) -> Book:
    ebook = epub.read_epub(str(path), options={"ignore_ncx": True})
    title = (ebook.get_metadata("DC", "title") or [("Untitled", {})])[0][0]
    author = (ebook.get_metadata("DC", "creator") or [("", {})])[0][0]
    chapters: list[Chapter] = []
    for item in ebook.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "html.parser")
        heading = soup.find(["h1", "h2", "h3"])
        paras = clean_paragraphs([p.get_text(" ") for p in soup.find_all("p")])
        if len(paras) < 2:
            continue  # cover, toc, copyright stubs
        chapters.append(
            Chapter(
                index=len(chapters) + 1,
                title=heading.get_text(" ", strip=True) if heading else f"Chapter {len(chapters) + 1}",
                paragraphs=paras,
            )
        )
    return Book(title=title, author=author, chapters=chapters)
