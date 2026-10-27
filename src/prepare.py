"""Prepare evidence notes from immutable raw feed files.

Case Bank rows are already curated, so they are copied deterministically.
Digests require an LLM extraction pass, split into arc-neutral theme packets.
This is source preparation, not a creative agent.

Usage: uv run python -m src.prepare
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

import yaml

from src.evidence import (
    evidence_db_id,
    load_manifest,
    manifest_path as default_manifest_path,
    save_manifest,
)
from src.llm import complete
from src.notion_io import Notion, date as d_prop, multi_select, select, title
from src.notion_setup import md_to_blocks

REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = REPO_ROOT / "prompts" / "digest_extractor.md"
STORYBOOK_PATH = REPO_ROOT / "storybook" / "state.md"
CASEBANK_LABELS = ("What happened", "Thesis tie", "Post angle", "Caution", "Source")
DIGEST_LIST_FIELDS = (
    "claims", "objections", "open_questions", "tensions", "examples",
    "quotes", "numbers", "cautions", "beats",
)


def parse_raw(path: Path) -> tuple[dict, str]:
    """Split a raw drop into (front-matter dict, body)."""
    text = path.read_text()
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        return yaml.safe_load(fm) or {}, body.strip()
    return {}, text.strip()


def _clean_tags(tags: list) -> list[str]:
    """Notion multi_select option names must not contain commas."""
    return [t.replace(",", " ·").strip() for t in tags if t and t.strip()]


def storybook_chapters(state: str) -> list[str]:
    """Read exact chapter names from the arc table, not the current chapter."""
    return [
        match.strip()
        for match in re.findall(
            r"(?m)^\|[^|\n]+\|\s*(\d+\s*·[^|\n]+?)\s*\|", state
        )
    ]


def _metadata_markdown(meta: dict, rel: str) -> str:
    lines = [f"- Raw path: feed/raw/{rel}"]
    for key, label in (
        ("area", "Area"),
        ("chapters", "Curated chapters"),
        ("flags", "Flags"),
        ("article", "Article"),
        ("period_start", "Period start"),
    ):
        value = meta.get(key)
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value)
        if value:
            lines.append(f"- {label}: {value}")
    return "## Source metadata\n" + "\n".join(lines)


def _casebank_sections(body: str) -> dict[str, str]:
    labels = "|".join(re.escape(label) for label in CASEBANK_LABELS)
    matches = list(re.finditer(rf"(?m)^\*\*({labels}):\*\*\s*", body))
    if not matches:
        return {"Source material": body.strip()}
    sections = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[match.group(1)] = body[match.end():end].strip()
    return sections


def render_casebank_note(meta: dict, body: str, rel: str) -> str:
    """Preserve the curated Case Bank packet without an LLM rewrite."""
    parts = [_metadata_markdown(meta, rel)]
    sections = _casebank_sections(body)
    for label in (*CASEBANK_LABELS, "Source material"):
        if sections.get(label):
            parts.append(f"## {label}\n{sections[label]}")
    return "\n\n".join(parts)


def parse_digest_json(raw: str, valid_beats: list[str],
                      source_text: str = "") -> list[dict]:
    """Parse and validate arc-neutral theme packets from the extractor."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    data = json.loads(text)
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("Digest extraction must be a JSON array")

    allowed = set(valid_beats)
    for packet in data:
        if not isinstance(packet, dict) or not str(packet.get("theme", "")).strip():
            raise ValueError("Every digest packet needs a non-empty theme")
        for key in DIGEST_LIST_FIELDS:
            packet.setdefault(key, [])
            if not isinstance(packet[key], list):
                raise ValueError(f"{key} must be a list")
        packet.setdefault("why_it_matters", "")
        for quote in packet["quotes"]:
            if not isinstance(quote, dict) or not str(quote.get("text", "")).strip():
                raise ValueError("Every quote needs verbatim text")
            quote.setdefault("speaker", "")
            if source_text and quote["text"] not in source_text:
                raise ValueError("Quote is not a verbatim substring of the digest")
        invalid = [beat for beat in packet["beats"] if beat not in allowed]
        if invalid:
            raise ValueError("Unknown storybook chapters: " + ", ".join(invalid))
    return data


def render_digest_note(packet: dict, meta: dict, rel: str) -> str:
    parts = [_metadata_markdown(meta, rel)]
    for key, heading in (
        ("claims", "Claims"),
        ("objections", "Objections"),
        ("open_questions", "Open questions"),
        ("tensions", "Tensions"),
        ("examples", "Examples"),
        ("numbers", "Numbers and conditions"),
        ("cautions", "Cautions"),
    ):
        items = packet.get(key, [])
        if items:
            parts.append(f"## {heading}\n" + "\n".join(f"- {i}" for i in items))
    quotes = packet.get("quotes", [])
    if quotes:
        lines = [
            f"- {quote['text']}"
            + (f" — {quote['speaker']}" if quote.get("speaker") else "")
            for quote in quotes
        ]
        parts.append("## Quotations\n" + "\n".join(lines))
    if packet.get("why_it_matters"):
        parts.append(f"## Why it matters\n{packet['why_it_matters']}")
    return "\n\n".join(parts)


def _create_note(notion, db_id: str, name: str, source: str, day: str,
                 beats: list[str], markdown: str) -> str:
    page_id = notion.create_page(
        {"database_id": db_id},
        {
            "Name": title(name),
            "Source": select(source),
            "Date": d_prop(day),
            "Beats": multi_select(_clean_tags(beats)),
        },
    )
    blocks = md_to_blocks(markdown)
    for index in range(0, len(blocks), 100):
        notion.append_blocks(page_id, blocks[index:index + 100])
    return page_id


def run(feed_dir: Path, manifest_file: Path, notion,
        llm_complete=complete, storybook_state: str | None = None,
        evidence_notes_db_id: str | None = None) -> int:
    db_id = evidence_notes_db_id or _evidence_db_id()
    manifest = load_manifest(manifest_file)
    prompt = PROMPT_PATH.read_text()
    state = storybook_state
    if state is None and STORYBOOK_PATH.exists():
        state = STORYBOOK_PATH.read_text()
    chapters = storybook_chapters(state or "")

    failures = []
    limit = int(os.environ.get("PREPARE_LIMIT", "0") or 0)
    prepared = 0
    for raw_file in sorted(feed_dir.glob("raw/*/*.md")):
        rel = str(raw_file.relative_to(feed_dir / "raw"))
        if rel in manifest:
            continue
        if limit and prepared >= limit:
            break
        try:
            meta, body = parse_raw(raw_file)
            source = meta.get("source", raw_file.parent.name)
            day = str(meta.get("date", date.today().isoformat()))
            page_ids = []
            if source == "casebank":
                markdown = render_casebank_note(meta, body, rel)
                page_ids.append(_create_note(
                    notion, db_id,
                    f"{source} · {day} · {raw_file.stem}",
                    source, day, meta.get("chapters", []), markdown,
                ))
            elif source == "digest":
                user = (
                    f"Storybook chapter vocabulary:\n{state or '(none)'}\n\n"
                    f"Raw file ({rel}, including front matter):\n{raw_file.read_text()}"
                )
                try:
                    packets = parse_digest_json(
                        llm_complete(prompt, user), chapters, raw_file.read_text()
                    )
                except (json.JSONDecodeError, ValueError) as exc:
                    raise RuntimeError(f"Invalid digest extraction: {exc}") from exc
                for packet in packets:
                    page_ids.append(_create_note(
                        notion, db_id,
                        f"{source} · {day} · {raw_file.stem} · {packet['theme']}",
                        source, day, packet["beats"],
                        render_digest_note(packet, meta, rel),
                    ))
            else:
                raise RuntimeError(f"Unsupported source type: {source}")

            manifest[rel] = page_ids
            save_manifest(manifest_file, manifest)
            prepared += 1
            print(f"prepared {rel} -> {len(page_ids)} evidence note(s)")
        except RuntimeError as exc:
            print(f"FAIL {rel}: {exc}")
            failures.append(rel)

    return 1 if failures else 0


def _evidence_db_id() -> str:
    ids = json.loads((REPO_ROOT / "notion_ids.json").read_text())
    return evidence_db_id(ids)


def main() -> int:
    feed_dir = REPO_ROOT / "feed"
    return run(feed_dir, default_manifest_path(feed_dir), Notion())


if __name__ == "__main__":
    sys.exit(main())
