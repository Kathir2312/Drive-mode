import json
import re
from pathlib import Path

import typer

from .ingest import read_book
from .config import DEFAULT_VOICES
from .models import MODES, TONES, BookConfig

app = typer.Typer(help="Ebook -> Tamil/English audiobook")
BOOKS = Path("books")


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "book"


@app.command()
def ingest(
    path: Path,
    source_lang: str = typer.Option("en", help="en | ta"),
    mode: str = typer.Option("narrate", help="narrate | translate"),
    rights: str = typer.Option("owned"),
):
    """Parse an ebook into books/<slug>/source.json."""
    if mode not in MODES:
        raise typer.BadParameter(f"mode must be one of {MODES}")
    book = read_book(path)
    slug = slugify(book.title)
    folder = BOOKS / slug
    folder.mkdir(parents=True, exist_ok=True)
    BookConfig(
        slug, book.title, book.author, source_lang, mode, None, rights, dict(DEFAULT_VOICES)
    ).save(folder)
    (folder / "source.json").write_text(
        json.dumps([c.__dict__ for c in book.chapters], ensure_ascii=False, indent=2)
    )
    typer.echo(f"{book.title}: {len(book.chapters)} chapters -> {folder}")


def ask_tone() -> str:
    typer.echo("Choose Tamil tone:\n  1) contemporary - everyday spoken Tamil\n  2) author - original author's tone")
    return {"1": "contemporary", "2": "author"}[typer.prompt("Tone", type=click_choice())]


def click_choice():
    import click
    return click.Choice(["1", "2"])


@app.command()
def translate(
    folder: Path,
    tone: str = typer.Option(None, help="contemporary | author (skips prompt)"),
    limit: int = typer.Option(0, help="Only first N chapters (0 = all)"),
):
    """Translate/modernize into Tamil. Asks for tone unless already set."""
    from .translate.engine import translate_chapter
    from .translate.glossary import load_glossary
    from .models import Chapter

    cfg = BookConfig.load(folder)
    if cfg.mode != "translate":
        typer.echo("Mode is narrate: nothing to translate.")
        raise typer.Exit()
    tone = tone or cfg.tone or ask_tone()
    if tone not in TONES:
        raise typer.BadParameter(f"tone must be one of {TONES}")
    cfg.tone = tone
    cfg.save(folder)
    chapters = [Chapter(**c) for c in json.loads((folder / "source.json").read_text())]
    glossary = load_glossary(folder)
    out = []
    for ch in chapters[: limit or None]:
        typer.echo(f"Translating {ch.index}: {ch.title}")
        out.append({"index": ch.index, "title": ch.title, "paragraphs": translate_chapter(ch, tone, glossary)})
    (folder / "target.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
