import re
from pathlib import Path

from .base import TTSProvider, cache_key
from .normalize import normalize

MAX_CHUNK = 2500
_SENTENCE_END = re.compile(r"(?<=[.!?।])\s+")


def chunk_text(text: str, max_chars: int = MAX_CHUNK) -> list[str]:
    """Split one paragraph at sentence boundaries into pieces of at most max_chars."""
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    cur = ""
    for sentence in _SENTENCE_END.split(text):
        while len(sentence) > max_chars:  # no punctuation: hard split on a space
            cut = sentence.rfind(" ", 0, max_chars) or max_chars
            chunks.append(sentence[:cut].strip())
            sentence = sentence[cut:].strip()
        if cur and len(cur) + 1 + len(sentence) > max_chars:
            chunks.append(cur)
            cur = sentence
        else:
            cur = f"{cur} {sentence}".strip()
    if cur:
        chunks.append(cur)
    return chunks


def count_chars(paragraphs: list[str], lang: str) -> int:
    return sum(len(c) for p in paragraphs for c in chunk_text(normalize(p, lang)))


def synthesize_paragraphs(
    provider: TTSProvider, paragraphs: list[str], voice: str, lang: str, cache_dir: Path
) -> list[Path]:
    """One MP3 per paragraph (chunks joined later); identical text is never paid for twice."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for para in paragraphs:
        for chunk in chunk_text(normalize(para, lang)):
            path = cache_dir / f"{cache_key(provider.name, voice, lang, chunk)}.mp3"
            if not path.exists():
                path.write_bytes(provider.synthesize(chunk, voice, lang))
            paths.append(path)
    return paths
