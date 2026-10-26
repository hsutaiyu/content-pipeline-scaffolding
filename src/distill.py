"""Distiller stage: raw feed files -> Distilled Notes rows in Notion.

Usage: uv run python -m src.distill
Requires: NOTION_API_KEY, NOTION_ROOT_PAGE_ID (or notion_ids.json),
          LLM_BASE_URL, LLM_API_KEY, LLM_MODEL.
"""

import json
import sys
from datetime import date
from pathlib import Path

import yaml

from src.llm import complete
from src.notion_io import Notion, date as d_prop, multi_select, paragraph, select, title
from src.notion_setup import md_to_blocks

REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = REPO_ROOT / "prompts" / "distiller.md"
STORYBOOK_PATH = REPO_ROOT / "storybook" / "state.md"


def parse_raw(path: Path) -> tuple[dict, str]:
    """Split a raw drop into (front-matter dict, body)."""
    text = path.read_text()
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        return yaml.safe_load(fm) or {}, body.strip()
    return {}, text.strip()


def render_note_markdown(data: dict) -> str:
    sections = [
        ("Claims", data.get("claims", [])),
        ("Case studies", data.get("case_studies", [])),
        ("Quotable lines", data.get("quotable_lines", [])),
    ]
    parts = []
    for heading, items in sections:
        if items:
            parts.append(f"## {heading}\n" + "\n".join(f"- {i}" for i in items))
    if data.get("why_it_matters"):
        parts.append(f"## Why it matters\n{data['why_it_matters']}")
    return "\n\n".join(parts)


def parse_llm_json(raw: str) -> dict:
    """Strict JSON out of an LLM reply; tolerates code fences only."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    data = json.loads(text)
    for key in ("claims", "case_studies", "quotable_lines", "beats"):
        data.setdefault(key, [])
    data.setdefault("why_it_matters", "")
    return data


def _clean_tags(tags: list) -> list[str]:
    """Notion multi_select option names must not contain commas."""
    return [t.replace(",", " ·").strip() for t in tags if t and t.strip()]


def run(feed_dir: Path, manifest_path: Path, notion,
        llm_complete=complete, storybook_state: str | None = None,
        distilled_db_id: str | None = None) -> int:
    db_id = distilled_db_id or _distilled_db_id()
    manifest = json.loads(manifest_path.read_text()) \
        if manifest_path.exists() else {}
    prompt = PROMPT_PATH.read_text()
    state = storybook_state
    if state is None and STORYBOOK_PATH.exists():
        state = STORYBOOK_PATH.read_text()

    failures = []
    for raw_file in sorted(feed_dir.glob("raw/*/*.md")):
        rel = str(raw_file.relative_to(feed_dir))
        if rel.startswith("raw/"):
            rel = rel[4:]
        if rel in manifest:
            continue
        try:
            meta, body = parse_raw(raw_file)
            source = meta.get("source", raw_file.parent.name)
            day = str(meta.get("date", date.today().isoformat()))
            user = (f"Storybook state:\n{state or '(none)'}\n\n"
                    f"Raw file ({rel}):\n{body}")
            try:
                data = parse_llm_json(llm_complete(prompt, user))
            except (json.JSONDecodeError, ValueError) as e:
                raise RuntimeError(f"LLM output was not valid JSON ({e})")
            page_id = notion.create_page(
                {"database_id": db_id},
                {
                    "Name": title(f"{source} · {day} · {raw_file.stem}"),
                    "Source": select(source),
                    "Date": d_prop(day),
                    "Beats": multi_select(_clean_tags(data["beats"])),
                },
            )
            md = render_note_markdown(data)
            if md:
                notion.append_blocks(page_id, md_to_blocks(md))
            manifest[rel] = page_id
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
            print(f"distilled {rel} -> {page_id}")
        except RuntimeError as e:
            print(f"FAIL {rel}: {e}")
            failures.append(rel)

    return 1 if failures else 0


def _distilled_db_id() -> str:
    ids = json.loads((REPO_ROOT / "notion_ids.json").read_text())
    return ids["distilled_notes_db"]


def main() -> int:
    notion = Notion()
    return run(Path("feed"), Path("feed/distilled-manifest.json"), notion)


if __name__ == "__main__":
    sys.exit(main())
