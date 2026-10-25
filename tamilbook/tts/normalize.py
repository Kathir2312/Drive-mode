import re

_TA_DIGITS = str.maketrans("0123456789", "௦௧௨௩௪௫௬௭௮௯")


def normalize_en(text: str) -> str:
    text = re.sub(r"\bMr\.", "Mister", text)
    text = re.sub(r"\bMrs\.", "Missus", text)
    text = re.sub(r"\bDr\.", "Doctor", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_ta(text: str) -> str:
    """Light cleanup; number/date/currency expansion arrives with the TTS bake-off."""
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize(text: str, lang: str) -> str:
    return normalize_ta(text) if lang == "ta" else normalize_en(text)
