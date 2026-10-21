"""Shared helper: drop a dated raw file into feed/raw/<source>/."""

import re
from pathlib import Path

import yaml


def slugify(text: str) -> str:
    s = re.sub(r"[’']", "", text.lower())
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60]


def write_raw(feed_dir: Path, source: str, day: str, slug: str,
              frontmatter: dict, body: str) -> Path:
    out_dir = feed_dir / "raw" / source
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{day}-{slugify(slug)}.md"
    fm = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    path.write_text(f"---\n{fm}\n---\n\n{body.strip()}\n")
    return path
