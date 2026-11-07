# Voices chosen in the M0 voice comparison (ElevenLabs).
DEFAULT_VOICES = {
    "ta": "a49ffQsGpRBw28CL67GF",  # Yazhini - Calm & Expressive Storyteller
    "en": "PWJQt7aZp1BOOvtsV5vv",  # Sara - intimate & warm
}
TTS_PROVIDER = "elevenlabs"
TTS_MODEL = "eleven_multilingual_v2"

# Default voice per provider and language. Books store ElevenLabs ids in book.yaml;
# other providers use these unless --voice is given.
PROVIDER_VOICES = {
    "elevenlabs": DEFAULT_VOICES,
    "azure": {"ta": "ta-IN-PallaviNeural", "en": "en-US-JennyNeural"},
}
AZURE_REGION = "centralindia"  # overridden by the AZURE_SPEECH_REGION environment variable
