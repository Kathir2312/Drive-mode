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
        "Preserve the original author's voice: period diction, imagery, sentence rhythm and "
        "formality. Choose Tamil equivalents that carry the same feel; do not flatten the style "
        "into modern colloquial speech, but keep it listenable."
    ),
}


def system_prompt(tone: str) -> str:
    if tone not in TONES:
        raise ValueError(f"tone must be one of {sorted(TONES)}")
    return f"{BASE}\n\n{TONES[tone]}"
