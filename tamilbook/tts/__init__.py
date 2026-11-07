from .base import TTSProvider


def get_provider(name: str) -> TTSProvider:
    if name == "elevenlabs":
        from .elevenlabs import ElevenLabs

        return ElevenLabs()
    if name == "azure":
        from .azure import Azure

        return Azure()
    raise ValueError(f"Unknown TTS provider {name!r}")
