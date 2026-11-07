import json
import re
from pathlib import Path

import typer

from .ingest import read_book
from .config import DEFAULT_VOICES, PROVIDER_VOICES, TTS_PROVIDER
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


def load_text_chapters(folder: Path, cfg: BookConfig) -> list[dict]:
    """Translated text if the book was translated, otherwise the source text."""
    target = folder / "target.json"
    if cfg.mode == "translate":
        if not target.exists():
            raise typer.BadParameter("Run `tamilbook translate` first (no target.json).")
        return json.loads(target.read_text())
    return json.loads((folder / "source.json").read_text())


@app.command()
def tts(
    folder: Path,
    limit: int = typer.Option(0, help="Only first N chapters (0 = all)"),
    yes: bool = typer.Option(False, "--yes", help="Skip the cost confirmation"),
    provider: str = typer.Option(TTS_PROVIDER, help="elevenlabs | azure"),
    voice: str = typer.Option(None, help="Voice id/name (default: the provider's default for the language)"),
    audio_dir: str = typer.Option("audio", help="Output folder inside the book folder"),
):
    """Synthesize speech per chapter into <folder>/audio/chapter_NN.mp3."""
    from .audio.master import join_chapter
    from .tts import get_provider
    from .tts.synth import count_chars, synthesize_paragraphs

    cfg = BookConfig.load(folder)
    lang = cfg.target_lang
    if provider == TTS_PROVIDER:
        voice = voice or cfg.voices.get(lang) or DEFAULT_VOICES[lang]
    else:
        voice = voice or PROVIDER_VOICES[provider][lang]
    chapters = load_text_chapters(folder, cfg)[: limit or None]
    chars = sum(count_chars(c["paragraphs"], lang) for c in chapters)
    typer.echo(f"{len(chapters)} chapters, {chars:,} characters, {provider} voice {voice} ({lang}).")
    if provider == "elevenlabs":
        typer.echo(f"Estimated cost: about {chars:,} ElevenLabs credits (~1 credit per character; cached text is free).")
    else:
        typer.echo(f"{provider}: billed per character against your plan or free tier; cached text is free.")
    if not yes:
        typer.confirm("Proceed?", abort=True)
    tts_provider = get_provider(provider)
    for ch in chapters:
        out = folder / audio_dir / f"chapter_{ch['index']:02d}.mp3"
        typer.echo(f"Chapter {ch['index']}: {ch['title']}")
        parts = synthesize_paragraphs(tts_provider, ch["paragraphs"], voice, lang, folder / "cache")
        join_chapter(parts, out)


@app.command()
def build(folder: Path, audio_dir: str = typer.Option("audio", help="Folder with chapter MP3s")):
    """Combine chapter MP3s into <folder>/<slug>.m4b with chapter markers."""
    from .audio.master import make_m4b

    cfg = BookConfig.load(folder)
    titles = {c["index"]: c["title"] for c in load_text_chapters(folder, cfg)}
    files = sorted((folder / audio_dir).glob("chapter_*.mp3"))
    if not files:
        raise typer.BadParameter("No audio found; run `tamilbook tts` first.")
    chapters = [(titles.get(int(f.stem.split("_")[1]), f.stem), f) for f in files]
    out = make_m4b(chapters, folder / f"{cfg.slug}-{cfg.target_lang}.m4b", cfg.title, cfg.author)
    typer.echo(f"Wrote {out}")


if __name__ == "__main__":
    app()
