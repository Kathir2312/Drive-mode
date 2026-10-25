import hashlib
from typing import Protocol


class TTSProvider(Protocol):
    name: str

    def synthesize(self, text: str, voice: str, lang: str) -> bytes:
        """Return MP3 bytes for text."""


def cache_key(provider: str, voice: str, lang: str, text: str) -> str:
    return hashlib.sha256(f"{provider}|{voice}|{lang}|{text}".encode()).hexdigest()
