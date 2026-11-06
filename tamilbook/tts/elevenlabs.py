import os

import httpx

from ..config import TTS_MODEL

API = "https://api.elevenlabs.io/v1/text-to-speech"


class ElevenLabs:
    name = "elevenlabs"

    def __init__(self, model: str = TTS_MODEL, api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY", "")

    def synthesize(self, text: str, voice: str, lang: str) -> bytes:
        headers = {"xi-api-key": self.api_key} if self.api_key else {}
        resp = httpx.post(
            f"{API}/{voice}",
            params={"output_format": "mp3_44100_128"},
            headers=headers,
            json={"text": text, "model_id": self.model},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.content
