import os

from ..models import Chapter
from .glossary import render_glossary
from .style import system_prompt

MODEL = os.environ.get("TAMILBOOK_MODEL", "claude-sonnet-5-5")
MAX_CHARS = 6000


def chunk_paragraphs(paragraphs: list[str], max_chars: int = MAX_CHARS) -> list[list[str]]:
    chunks: list[list[str]] = []
    cur: list[str] = []
    size = 0
    for p in paragraphs:
        if cur and size + len(p) > max_chars:
            chunks.append(cur)
            cur, size = [], 0
        cur.append(p)
        size += len(p)
    if cur:
        chunks.append(cur)
    return chunks


def translate_chapter(chapter: Chapter, tone: str, glossary: dict[str, str], summary: str = "") -> list[str]:
    import anthropic

    client = anthropic.Anthropic()
    system = "\n\n".join(filter(None, [system_prompt(tone), render_glossary(glossary)]))
    out: list[str] = []
    for chunk in chunk_paragraphs(chapter.paragraphs):
        context = f"Story so far: {summary}\n\n" if summary else ""
        msg = client.messages.create(
            model=MODEL,
            max_tokens=8000,
            system=system,
            messages=[{
                "role": "user",
                "content": f"{context}Translate each paragraph; return one Tamil paragraph per line, "
                "same count and order, separated by blank lines.\n\n" + "\n\n".join(chunk),
            }],
        )
        text = msg.content[0].text.strip()
        out.extend(p.strip() for p in text.split("\n\n") if p.strip())
    return out
