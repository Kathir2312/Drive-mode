from .base import TTSProvider


def get_provider(name: str) -> TTSProvider:
    if name == "elevenlabs":
        from .elevenlabs import ElevenLabs

        return ElevenLabs()
    raise ValueError(f"Unknown TTS provider {name!r}")
