BASE = (
    "You translate books into Tamil for an audiobook that will be read aloud. "
    "Output only the Tamil text. Keep names consistent with the glossary. "
    "Where Tamil has no natural word, use the glossary term or a clear loan/coinage."
)

TONES = {
    "contemporary": (
        "Use everyday contemporary spoken Tamil (பேச்சுத் தமிழ்): modern idiom, short natural "
        "sentences, easy to follow when heard."
    ),
    "author": (
        "Preserve the original author's voice: formal, precise sentence structure, long "
        "sentences where the author uses them, period feel and imagery. Write in modern "
        "standard written Tamil, not archaic or classical Tamil: prefer words in current "
        "use (ரோமம், மேஜை, ஜன்னல், ரயில்) over pure-Tamil coinages or old forms "
        "(உரோமம், etc.). Do not use colloquial spoken forms either; keep it listenable."
    ),
}


def system_prompt(tone: str) -> str:
    if tone not in TONES:
        raise ValueError(f"tone must be one of {sorted(TONES)}")
    return f"{BASE}\n\n{TONES[tone]}"
