# tamilbook

Personal tool to turn ebooks into audiobooks:

1. Tamil ebook -> Tamil audio
2. English ebook -> Tamil audio (choose *contemporary* or *original author's* tone)
3. English ebook -> English audio

Plan: see the approved plan (ingest -> translate -> tts -> master -> package -> feed).

    pip install -e '.[dev]'
    tamilbook ingest mybook.epub --source-lang en --mode translate
    tamilbook translate books/mybook          # asks for tone

## Making audio

    export ELEVENLABS_API_KEY=...        # or put it in .env
    tamilbook tts books/mybook           # shows character/credit estimate, asks to proceed
    tamilbook build books/mybook         # -> books/mybook/mybook-<lang>.m4b with chapters

`tts --limit 1` is a cheap way to test one chapter first. Identical text is cached in
`books/<slug>/cache/`, so re-runs only pay for changed paragraphs.

## Other voice providers

    tamilbook tts books/mybook --provider azure --audio-dir audio_azure --yes

Azure uses `AZURE_SPEECH_REGION` (default `centralindia`) and, outside a managed environment,
`AZURE_SPEECH_KEY`. Voices default to `ta-IN-PallaviNeural` (Tamil) and `en-US-JennyNeural`
(English); override with `--voice ta-IN-ValluvarNeural`. `build --audio-dir audio_azure`
assembles that recording.
