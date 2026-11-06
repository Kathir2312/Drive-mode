import json

from typer.testing import CliRunner

from tamilbook.cli import app
from tamilbook.ingest.clean import clean_paragraphs
from tamilbook.ingest.txt import read_txt
from tamilbook.models import BookConfig
from tamilbook.translate.engine import chunk_paragraphs
from tamilbook.translate.glossary import render_glossary
from tamilbook.translate.style import system_prompt
from tamilbook.tts.base import cache_key
from tamilbook.tts.normalize import normalize


def test_clean_drops_page_numbers():
    assert clean_paragraphs(["  12 ", "Hello   world", "Page 4"]) == ["Hello world"]


def test_txt_chapters(tmp_path):
    f = tmp_path / "b.txt"
    f.write_text("Chapter 1\n\nA.\n\nB.\n\nChapter 2\n\nC.")
    book = read_txt(f)
    assert [len(c.paragraphs) for c in book.chapters] == [2, 1]


def test_target_lang():
    assert BookConfig("s", "t", source_lang="en", mode="translate").target_lang == "ta"
    assert BookConfig("s", "t", source_lang="en", mode="narrate").target_lang == "en"
    assert BookConfig("s", "t", source_lang="ta", mode="narrate").target_lang == "ta"


def test_tone_prompts_differ():
    assert system_prompt("contemporary") != system_prompt("author")


def test_glossary_render():
    assert "Darcy => டார்சி" in render_glossary({"Darcy": "டார்சி"})


def test_chunking():
    chunks = chunk_paragraphs(["a" * 60, "b" * 60, "c" * 60], max_chars=100)
    assert [len(c) for c in chunks] == [1, 1, 1]


def test_cache_key_stable():
    assert cache_key("a", "v", "ta", "x") == cache_key("a", "v", "ta", "x") != cache_key("a", "v", "en", "x")


def test_normalize_en():
    assert normalize("Mr. Smith", "en") == "Mister Smith"


def test_ingest_cli(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "bk.txt").write_text("Chapter 1\n\nOne.\n\nTwo.")
    r = CliRunner().invoke(app, ["ingest", "bk.txt", "--source-lang", "en", "--mode", "translate"])
    assert r.exit_code == 0, r.output
    assert json.loads((tmp_path / "books/bk/source.json").read_text())[0]["paragraphs"] == ["One.", "Two."]


def test_ingest_saves_default_voices(tmp_path, monkeypatch):
    from tamilbook.config import DEFAULT_VOICES

    monkeypatch.chdir(tmp_path)
    (tmp_path / "bk.txt").write_text("Chapter 1\n\nOne.\n\nTwo.")
    CliRunner().invoke(app, ["ingest", "bk.txt"])
    cfg = BookConfig.load(tmp_path / "books/bk")
    assert cfg.voices == DEFAULT_VOICES
