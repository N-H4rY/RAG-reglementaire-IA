"""Extraction du texte des PDF (PyMuPDF), nettoyage et métadonnées."""
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import pymupdf

from src.config import load_config

ARTICLE_RE = re.compile(r"^\s*Article\s+(\d+(?:\s?bis)?)\s*$", re.M)


@dataclass
class Page:
    doc: str
    page: int          # numéro de page, à partir de 1
    text: str
    article_start: str | None  # article en cours au début de la page
    articles: list[str]        # articles dont le titre figure sur la page


def _repeated_lines(pages: list[str], ratio: float) -> set[str]:
    """Lignes répétées sur une grande part des pages (en-têtes, pieds de page)."""
    if len(pages) < 4:
        return set()
    counts = Counter(l.strip() for p in pages for l in set(p.splitlines()) if l.strip())
    return {l for l, c in counts.items() if c / len(pages) > ratio}


def clean(text: str, repeated: set[str]) -> str:
    lines = [l for l in text.splitlines() if l.strip() not in repeated]
    text = "\n".join(lines)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)   # mots coupés en fin de ligne
    text = re.sub(r"[ \t\u00a0]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def ingest_pdf(path: Path, cfg: dict) -> list[Page]:
    with pymupdf.open(path) as pdf:
        raw = [p.get_text("text") for p in pdf]
    repeated = _repeated_lines(raw, cfg["ingestion"]["header_footer_min_ratio"])
    pages, current = [], None
    for i, text in enumerate(raw, start=1):
        text = clean(text, repeated)
        found = [m.group(1) for m in ARTICLE_RE.finditer(text)]
        pages.append(Page(doc=path.stem, page=i, text=text, article_start=current, articles=found))
        current = found[-1] if found else current
    return pages


def ingest_all(cfg: dict | None = None) -> dict[str, list[Page]]:
    cfg = cfg or load_config()
    return {p.stem: ingest_pdf(p, cfg) for p in sorted(cfg["paths"]["raw"].glob("*.pdf"))}


def stats(docs: dict[str, list[Page]], cfg: dict) -> list[dict]:
    rows = []
    for name, pages in docs.items():
        chars = sum(len(p.text) for p in pages)
        empty = sum(1 for p in pages if len(p.text) < 20)
        avg = chars / max(len(pages), 1)
        rows.append({
            "doc": name, "pages": len(pages), "chars": chars,
            "chars_par_page": round(avg), "pages_vides": empty,
            "articles": len({a for p in pages for a in p.articles}),
            "scanne_suspecte": avg < cfg["ingestion"]["scanned_min_chars_per_page"],
        })
    return rows


def save(docs: dict[str, list[Page]], cfg: dict) -> Path:
    out = cfg["paths"]["processed"] / "pages.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for pages in docs.values():
            for p in pages:
                f.write(json.dumps(asdict(p), ensure_ascii=False) + "\n")
    return out


if __name__ == "__main__":
    cfg = load_config()
    docs = ingest_all(cfg)
    rows = stats(docs, cfg)
    print(f"{'document':32}{'pages':>6}{'caractères':>12}{'car/page':>9}{'vides':>6}{'art.':>6}  scan?")
    for r in rows:
        print(f"{r['doc']:32}{r['pages']:>6}{r['chars']:>12}{r['chars_par_page']:>9}"
              f"{r['pages_vides']:>6}{r['articles']:>6}  {'OUI' if r['scanne_suspecte'] else 'non'}")
    print(f"\nTotal : {sum(r['pages'] for r in rows)} pages, {sum(r['chars'] for r in rows)} caractères")
    print("Écrit :", save(docs, cfg).relative_to(cfg["paths"]["processed"].parents[1]))
