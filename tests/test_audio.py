import json
import shutil
import subprocess

import pytest
from typer.testing import CliRunner

from tamilbook import cli
from tamilbook.audio.master import duration
from tamilbook.tts.synth import chunk_text, count_chars, synthesize_paragraphs

pytestmark = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")


class FakeProvider:
    name = "fake"

    def __init__(self):
        self.calls = 0

    def synthesize(self, text, voice, lang):
        self.calls += 1
        out = subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", "sine=frequency=440:duration=0.5",
             "-f", "mp3", "-"], capture_output=True, check=True,
        )
        return out.stdout


def test_chunk_text_respects_limit():
    text = " ".join(f"Sentence number {i}." for i in range(200))
    chunks = chunk_text(text, max_chars=200)
    assert all(len(c) <= 200 for c in chunks)
    assert " ".join(chunks) == text


def test_chunk_text_handles_unpunctuated():
    chunks = chunk_text("word " * 100, max_chars=50)
    assert all(len(c) <= 50 for c in chunks) and len(chunks) > 1


def test_count_chars():
    assert count_chars(["Mr. Smith"], "en") == len("Mister Smith")


def test_cache_avoids_repeat_calls(tmp_path):
    p = FakeProvider()
    synthesize_paragraphs(p, ["Hello there.", "Hello there."], "v", "en", tmp_path)
    assert p.calls == 1


def test_tts_and_build_end_to_end(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fake = FakeProvider()
    monkeypatch.setattr("tamilbook.tts.get_provider", lambda name: fake)
    (tmp_path / "bk.txt").write_text("Chapter 1\n\nOne.\n\nTwo.\n\nChapter 2\n\nThree.")
    runner = CliRunner()
    assert runner.invoke(cli.app, ["ingest", "bk.txt"]).exit_code == 0
    r = runner.invoke(cli.app, ["tts", "books/bk", "--yes"])
    assert r.exit_code == 0, r.output
    assert "Estimated cost" in r.output
    audio = sorted((tmp_path / "books/bk/audio").glob("*.mp3"))
    assert len(audio) == 2 and all(duration(a) > 0.5 for a in audio)
    r = runner.invoke(cli.app, ["build", "books/bk"])
    assert r.exit_code == 0, r.output
    m4b = tmp_path / "books/bk/bk-en.m4b"
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_chapters", "-of", "json", str(m4b)],
        capture_output=True, text=True, check=True,
    )
    chapters = json.loads(probe.stdout)["chapters"]
    assert [c["tags"]["title"] for c in chapters] == ["Chapter 1", "Chapter 2"]
