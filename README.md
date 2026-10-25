# tamilbook

Personal tool to turn ebooks into audiobooks:

1. Tamil ebook -> Tamil audio
2. English ebook -> Tamil audio (choose *contemporary* or *original author's* tone)
3. English ebook -> English audio

Plan: see the approved plan (ingest -> translate -> tts -> master -> package -> feed).

    pip install -e '.[dev]'
    tamilbook ingest mybook.epub --source-lang en --mode translate
    tamilbook translate books/mybook          # asks for tone
