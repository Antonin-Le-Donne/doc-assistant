"""Stage 1: PDF → pages with metadata. See SPEC.md §5 (Page)."""

import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Iterator, TypedDict

import pymupdf

HEADING_MIN_RATIO = 1.35  # font size relative to body text
# Callouts and recommendation titles are set in large fonts too: real headings are numbered.
# A lone "I" is excluded: the Linux guide uses it as a hardening level tag (M, I, R, E).
NUMBERED_HEADING = re.compile(r"^(\d+(\.\d+)*|II|III|IV|V|VI|VII|VIII|IX|X|Annexe\s+\w+)(\s|$)")
MIN_REPEATED_KEY_LENGTH = 12  # keeps short per-measure labels such as "/Standard"


class Page(TypedDict):
    doc_id: str
    doc_title: str
    page: int
    section: str | None
    text: str


def make_doc_id(pdf_path: Path) -> str:
    """Stable slug from the file name (lowercase, no spaces or accents)."""
    ascii_name = unicodedata.normalize("NFKD", pdf_path.stem).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9_-]+", "_", ascii_name.lower()).strip("_")


def extract_pages(pdf_path: Path) -> Iterator[Page]:
    """Yield one Page per PDF page, 1-based page numbers.

    Section detection: track the most recent heading seen so far
    (headings are usually lines in a larger or bold font). A page holding
    several headings is labelled with its last one.
    """
    repeated_lines = find_repeated_lines(pdf_path)
    with pymupdf.open(pdf_path) as doc:
        doc_id = make_doc_id(pdf_path)
        title = _document_title(doc, pdf_path)
        body_size = _body_font_size(doc)
        section = None
        for number, pdf_page in enumerate(doc, start=1):
            blocks = _page_lines(pdf_page)
            headings = _find_headings(blocks, body_size, repeated_lines)
            if headings:
                section = headings[-1]
            raw_text = "\n\n".join("\n".join(text for text, _ in block) for block in blocks)
            yield Page(
                doc_id=doc_id,
                doc_title=title,
                page=number,
                section=section,
                text=clean_text(raw_text, repeated_lines),
            )


def clean_text(text: str, repeated_lines: set[str]) -> str:
    """Remove repeated headers/footers and fix broken hyphenation."""
    text = unicodedata.normalize("NFKC", text)
    kept = [line for line in text.split("\n") if _line_key(line) not in repeated_lines or not line.strip()]
    # Page numbers sit at the very top or bottom; measure numbers never do.
    while kept and (kept[0].strip().isdigit() or not kept[0].strip()):
        kept.pop(0)
    while kept and (kept[-1].strip().isdigit() or not kept[-1].strip()):
        kept.pop()
    # Decorative lines: ". " in some guides, and ">>" bullets alone on their line.
    kept = [line for line in kept if line.strip() != "."]
    cleaned = "\n".join(kept)
    cleaned = re.sub(r"^\s*>>\s*\n+\s*", "- ", cleaned, flags=re.M)
    cleaned = re.sub(r"(?<=\w)-[ \t]*\n[ \t]*(?=[a-zà-ÿ])", "", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r" ?\n ?", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def find_repeated_lines(pdf_path: Path, min_share: float = 0.5) -> set[str]:
    """Lines that appear on at least `min_share` of the pages (headers, footers)."""
    with pymupdf.open(pdf_path) as doc:
        page_count = doc.page_count
        counts: Counter[str] = Counter()
        for pdf_page in doc:
            counts.update({_line_key(line) for line in pdf_page.get_text().split("\n")})
    return {
        key
        for key, count in counts.items()
        if len(key) >= MIN_REPEATED_KEY_LENGTH and count / page_count >= min_share
    }


def _line_key(line: str) -> str:
    """Comparison key that ignores page numbers and punctuation ("8 – TITLE" = "TITLE – 9")."""
    return re.sub(r"[\W\d_]+", " ", unicodedata.normalize("NFKC", line)).strip().casefold()


def _page_lines(pdf_page) -> list[list[tuple[str, float]]]:
    """Text blocks of a page, each a list of (line text, largest font size)."""
    blocks = []
    for block in pdf_page.get_text("dict")["blocks"]:
        lines = []
        for line in block.get("lines", []):
            parts = [
                "- " if span["font"].startswith("Dingbats") else span["text"]
                for span in line["spans"]
            ]
            text = "".join(parts)
            if text.strip():
                lines.append((text, max(span["size"] for span in line["spans"])))
        if lines:
            blocks.append(lines)
    return blocks


def _find_headings(blocks, body_size: float, repeated_lines: set[str]) -> list[str]:
    """Headings of a page: a numbered large line ("2.1") plus the large lines after it (its title)."""
    headings = []
    current: list[str] = []
    for block in blocks:
        for text, size in block:
            text = text.strip()
            is_large = size >= body_size * HEADING_MIN_RATIO and _line_key(text) not in repeated_lines
            if is_large and NUMBERED_HEADING.match(text):
                # A new number closes the heading before it ("2 Title" then "2.1 Title").
                if len(current) > 1:
                    headings.append(" ".join(current))
                    current = []
                current.append(text)
            elif is_large and current:
                current.append(text)
            elif current:
                headings.append(" ".join(current))
                current = []
    if current:
        headings.append(" ".join(current))
    return headings


def _body_font_size(doc) -> float:
    """The font size holding the most characters in the document."""
    sizes: Counter[float] = Counter()
    for pdf_page in doc:
        for block in _page_lines(pdf_page):
            for text, size in block:
                sizes[round(size, 1)] += len(text)
    return sizes.most_common(1)[0][0] if sizes else 0.0


def _document_title(doc, pdf_path: Path) -> str:
    """PDF metadata title, else the largest text on the first page, else the file name."""
    title = (doc.metadata or {}).get("title", "").strip()
    if title:
        return title
    if doc.page_count:
        lines = [line for block in _page_lines(doc[0]) for line in block]
        if lines:
            largest = max(size for _, size in lines)
            title = " ".join(text.strip() for text, size in lines if size >= largest - 0.5)
    return re.sub(r"\s+", " ", title).strip() or pdf_path.stem
