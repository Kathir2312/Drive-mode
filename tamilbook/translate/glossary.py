from pathlib import Path

import yaml


def load_glossary(folder: Path) -> dict[str, str]:
    path = folder / "glossary.yaml"
    return yaml.safe_load(path.read_text()) or {} if path.exists() else {}


def render_glossary(entries: dict[str, str]) -> str:
    if not entries:
        return ""
    lines = "\n".join(f"- {k} => {v}" for k, v in entries.items())
    return f"Glossary (always use these renderings):\n{lines}"
