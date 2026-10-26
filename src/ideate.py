"""Ideator agent: narrative state + evidence + raw sources -> Idea Cards."""

import json
import re
import sys
from datetime import date
from pathlib import Path

from src.evidence import evidence_db_id, raw_sources_for_notes
from src.llm import complete
from src.notion_io import Notion, multi_select, relation, select, text, title
from src.notion_setup import md_to_blocks

REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = REPO_ROOT / "prompts" / "ideator.md"
IDS_PATH = REPO_ROOT / "notion_ids.json"


def parse_cards(raw: str) -> list[dict]:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    data = json.loads(text)
    return [data] if isinstance(data, dict) else data


def render_card_body(card: dict) -> str:
    lines = [f"**Hook:** {card['hook']}"]
    if card.get("central_tension"):
        lines += ["", f"**Central tension:** {card['central_tension']}"]
    if card.get("arc_fit"):
        lines += ["", f"**Why it serves the chapter:** {card['arc_fit']}"]
    lines += ["", "**Outline:**"]
    lines += [f"- {item}" for item in card.get("outline", [])]
    cautions = card.get("cautions", [])
    if cautions:
        lines += ["", "**Cautions (binding for drafting):**"]
        lines += [f"- {item}" for item in cautions]
    return "\n".join(lines)


def build_user_prompt(state: str, published_log: str, notes: list[dict],
                      existing_titles: list[str],
                      raw_sources: list[dict] | None = None) -> str:
    notes_block = "\n\n".join(
        f"### note id: {n['id']}\n"
        f"Title: {n.get('title', '')}\n"
        f"Source: {n.get('source', '')}\n"
        f"Date: {n.get('date', '')}\n"
        f"Beats: {', '.join(n.get('beats', [])) or '(none)'}\n"
        f"Raw paths: {', '.join(n.get('raw_paths', [])) or '(none)'}\n"
        f"{n.get('markdown', '')}"
        for n in notes
    )
    raw_block = "\n\n".join(
        f"### {source['path']}\n{source['text']}"
        for source in (raw_sources or [])
    )
    existing = "\n".join(f"- {t}" for t in existing_titles) or "(none)"
    return (
        f"## Storybook state\n{state}\n\n"
        f"## Published log\n{published_log}\n\n"
        f"## Existing idea card titles (do not re-propose)\n{existing}\n\n"
        f"## Evidence notes\n{notes_block or '(none)'}\n\n"
        f"## Original raw sources for candidate notes\n{raw_block or '(none)'}"
    )


def _note_title(row: dict) -> str:
    parts = row.get("properties", {}).get("Name", {}).get("title", [])
    return "".join(p.get("plain_text", "") for p in parts)


def _note_beats(row: dict) -> list[str]:
    values = row.get("properties", {}).get("Beats", {}).get("multi_select", [])
    return [value["name"] for value in values]


def _note_source(row: dict) -> str:
    value = row.get("properties", {}).get("Source", {}).get("select") or {}
    return value.get("name", "")


def _note_date(row: dict) -> str:
    value = row.get("properties", {}).get("Date", {}).get("date") or {}
    return value.get("start", "")


def current_chapter(state: str) -> str:
    match = re.search(
        r"(?m)^\s*-?\s*(?:\*\*)?Current chapter:(?:\*\*)?\s*(.+?)\s*$", state
    )
    return match.group(1).split(" (", 1)[0].strip() if match else ""


def _chapter_number(chapter: str) -> str:
    match = re.match(r"\s*(\d+)", chapter)
    return match.group(1) if match else ""


def _select_note_rows(rows: list[dict], state: str) -> list[dict]:
    """Shortlist by chapter number, tolerating punctuation in chapter names."""
    current = _chapter_number(current_chapter(state))
    if not current:
        return rows
    return [
        row for row in rows
        if current in {_chapter_number(beat) for beat in _note_beats(row)}
    ]


def run(notion: Notion, ids: dict, llm_complete=complete,
        feed_dir: Path = REPO_ROOT / "feed",
        manifest_file: Path | None = None) -> int:
    state = notion.get_page_markdown(ids["pages"]["Storybook / State"])
    log = notion.get_page_markdown(ids["pages"]["Storybook / Published Log"])

    rows = _select_note_rows(notion.query(evidence_db_id(ids)), state)
    notes = []
    for row in rows:
        notes.append({
            "id": row["id"],
            "title": _note_title(row),
            "source": _note_source(row),
            "date": _note_date(row),
            "beats": _note_beats(row),
            "markdown": notion.get_page_markdown(row["id"]),
        })
    raw_sources = raw_sources_for_notes(
        [note["id"] for note in notes], feed_dir, manifest_file
    )
    for note in notes:
        note["raw_paths"] = [
            source["path"] for source in raw_sources
            if note["id"] in source["note_ids"]
        ]

    existing = [_note_title(row) for row in notion.query(ids["idea_cards_db"])]
    user = build_user_prompt(state, log, notes, existing, raw_sources)
    cards = parse_cards(llm_complete(PROMPT_PATH.read_text(), user))

    for card in cards:
        notion.create_page(
            {"database_id": ids["idea_cards_db"]},
            {
                "Name": title(card["title"]),
                "Status": select("proposed"),
                "Review": select("pending"),
                "Chapter": text(card.get("chapter", "")),
                "Question": text(card.get("question", "")),
                "Beats": multi_select(card.get("beats", [])),
                "Format": select(card.get("format", "x-post")),
                "Sources": relation(card.get("source_note_ids", [])),
            },
            children=md_to_blocks(render_card_body(card)),
        )
        print(f"proposed: {card['title']}")

    summary = (
        f"- {date.today().isoformat()}: ideator proposed {len(cards)} card(s) "
        f"from {len(notes)} candidate evidence note(s)"
    )
    notion.append_blocks(ids["pages"]["Storybook / State"], md_to_blocks(summary))
    return 0


def main() -> int:
    ids = json.loads(IDS_PATH.read_text())
    return run(Notion(), ids)


if __name__ == "__main__":
    sys.exit(main())
