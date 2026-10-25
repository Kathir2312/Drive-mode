import re

_PAGE_NUM = re.compile(r"^\s*(page\s*)?\d{1,4}\s*$", re.IGNORECASE)


def clean_paragraphs(paragraphs: list[str]) -> list[str]:
    out = []
    for p in paragraphs:
        p = re.sub(r"\s+", " ", p).strip()
        if p and not _PAGE_NUM.match(p):
            out.append(p)
    return out
