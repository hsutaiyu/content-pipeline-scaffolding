"""Ideator stage: distilled notes + storybook state -> Idea Cards rows.

Usage: uv run python -m src.ideate
Requires: NOTION_API_KEY, notion_ids.json, LLM_BASE_URL, LLM_API_KEY, LLM_MODEL.
"""

import json
import sys
from datetime import date
from pathlib import Path

from src.llm import complete
from src.notion_io import (Notion, multi_select, relation, select, text, title)
from src.notion_setup import md_to_blocks

PROMPT_PATH = Path("prompts/ideator.md")
IDS_PATH = Path("notion_ids.json")


def parse_cards(raw: str) -> list[dict]:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    data = json.loads(text)
    return [data] if isinstance(data, dict) else data


def render_card_body(card: dict) -> str:
    lines = [f"**Hook:** {card['hook']}", "", "**Outline:**"]
    lines += [f"- {item}" for item in card.get("outline", [])]
    return "\n".join(lines)


def build_user_prompt(state: str, published_log: str, notes: list[dict],
                      existing_titles: list[str]) -> str:
    notes_block = "\n\n".join(
        f"### note id: {n['id']}\n{n.get('title', '')}\n{n.get('markdown', '')}"
        for n in notes)
    existing = "\n".join(f"- {t}" for t in existing_titles) or "(none)"
    return (
        f"## Storybook state\n{state}\n\n"
        f"## Published log\n{published_log}\n\n"
        f"## Existing idea card titles (do not re-propose)\n{existing}\n\n"
        f"## Distilled notes\n{notes_block or '(none)'}"
    )


def _note_title(row: dict) -> str:
    parts = row.get("properties", {}).get("Name", {}).get("title", [])
    return "".join(p.get("plain_text", "") for p in parts)


def run(notion: Notion, ids: dict, llm_complete=complete) -> int:
    state = notion.get_page_markdown(ids["pages"]["Storybook / State"])
    log = notion.get_page_markdown(ids["pages"]["Storybook / Published Log"])

    note_rows = notion.query(ids["distilled_notes_db"])
    notes = [{"id": r["id"], "title": _note_title(r),
              "markdown": notion.get_page_markdown(r["id"])}
             for r in note_rows]
    existing = [_note_title(r) for r in notion.query(ids["idea_cards_db"])]

    user = build_user_prompt(state, log, notes, existing)
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

    summary = (f"- {date.today().isoformat()}: ideator proposed "
               f"{len(cards)} card(s)")
    notion.append_blocks(ids["pages"]["Storybook / State"],
                         md_to_blocks(summary))
    return 0


def main() -> int:
    ids = json.loads(IDS_PATH.read_text())
    return run(Notion(), ids)


if __name__ == "__main__":
    sys.exit(main())
