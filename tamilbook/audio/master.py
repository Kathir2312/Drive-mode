import subprocess
import tempfile
from pathlib import Path

PAUSE_SECS = 0.6
LOUDNORM = "loudnorm=I=-16:TP=-1.5:LRA=11"


def _ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def _silence(path: Path, secs: float) -> Path:
    _ffmpeg("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(secs), "-c:a", "libmp3lame", "-q:a", "4", str(path))
    return path


def join_chapter(parts: list[Path], out: Path) -> Path:
    """Concatenate synthesized pieces with short pauses and normalize loudness to -16 LUFS."""
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        silence = _silence(Path(tmp) / "pause.mp3", PAUSE_SECS)
        listing = Path(tmp) / "list.txt"
        listing.write_text(
            "".join(f"file '{p.resolve()}'\nfile '{silence}'\n" for p in parts)
        )
        _ffmpeg("-f", "concat", "-safe", "0", "-i", str(listing), "-af", LOUDNORM,
                "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "96k", str(out))
    return out


def duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())


def make_m4b(chapters: list[tuple[str, Path]], out: Path, title: str, author: str) -> Path:
    """Single audiobook file with chapter markers from per-chapter MP3s."""
    with tempfile.TemporaryDirectory() as tmp:
        listing = Path(tmp) / "list.txt"
        listing.write_text("".join(f"file '{p.resolve()}'\n" for _, p in chapters))
        meta = [";FFMETADATA1", f"title={title}", f"artist={author}", "genre=Audiobook",
                "comment=AI-narrated audiobook"]
        start = 0.0
        for name, path in chapters:
            end = start + duration(path)
            meta += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(start * 1000)}",
                     f"END={int(end * 1000)}", f"title={name}"]
            start = end
        metafile = Path(tmp) / "meta.txt"
        metafile.write_text("\n".join(meta) + "\n")
        _ffmpeg("-f", "concat", "-safe", "0", "-i", str(listing), "-i", str(metafile),
                "-map_metadata", "1", "-map_chapters", "1", "-c:a", "aac", "-b:a", "64k",
                "-f", "ipod", str(out))
    return out
