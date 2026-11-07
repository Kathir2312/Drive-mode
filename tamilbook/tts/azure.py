import os
from xml.sax.saxutils import escape

import httpx

from ..config import AZURE_REGION

LOCALES = {"ta": "ta-IN", "en": "en-US"}
OUTPUT_FORMAT = "audio-24khz-96kbitrate-mono-mp3"


def build_ssml(text: str, voice: str, lang: str) -> str:
    return (
        f"<speak version='1.0' xml:lang='{LOCALES[lang]}' "
        "xmlns='http://www.w3.org/2001/10/synthesis'>"
        f"<voice name='{voice}'>{escape(text)}</voice></speak>"
    )


class Azure:
    name = "azure"

    def __init__(self, region: str | None = None, api_key: str | None = None):
        self.region = region or os.environ.get("AZURE_SPEECH_REGION") or AZURE_REGION
        self.api_key = api_key or os.environ.get("AZURE_SPEECH_KEY", "")

    def synthesize(self, text: str, voice: str, lang: str) -> bytes:
        # With a network secret on the environment the key header is added in transit;
        # AZURE_SPEECH_KEY is only needed when running outside it.
        headers = {
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": OUTPUT_FORMAT,
            "User-Agent": "tamilbook",
        }
        if self.api_key:
            headers["Ocp-Apim-Subscription-Key"] = self.api_key
        resp = httpx.post(
            f"https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1",
            headers=headers,
            content=build_ssml(text, voice, lang).encode("utf-8"),
            timeout=120,
        )
        resp.raise_for_status()
        return resp.content
