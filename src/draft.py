"""Drafter agent: chosen card + cited evidence/raw sources -> Notion draft."""

import argparse
import json
import sys
from pathlib import Path

from src.evidence import raw_sources_for_notes
from src.llm import complete
from src.notion_io import Notion, select
from src.notion_setup import md_to_blocks

REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = REPO_ROOT / "prompts" / "drafter.md"
IDS_PATH = REPO_ROOT / "notion_ids.json"
LINES_DIR = REPO_ROOT / "content-bank" / "lines"


def _plain_text(prop: dict) -> str:
    for key in ("title", "rich_text"):
        if key in prop:
            return "".join(t.get("plain_text", "") for t in prop[key])
    return ""


def card_from_row(row: dict) -> dict:
    props = row["properties"]
    return {
        "id": row["id"],
        "title": _plain_text(props["Name"]),
        "format": (props.get("Format", {}).get("select") or {}).get("name", ""),
        "chapter": _plain_text(props.get("Chapter", {})),
        "question": _plain_text(props.get("Question", {})),
        "sources": [
            relation["id"]
            for relation in props.get("Sources", {}).get("relation", [])
        ],
    }


def build_user_prompt(card: dict, notes_md: list[str], raw_sources: list[dict],
                      voice: str, fmt: str, lines_bank: str) -> str:
    notes = "\n\n".join(notes_md) or "(none)"
    raw = "\n\n".join(
        f"### {source['path']}\n{source['text']}" for source in raw_sources
    ) or "(none)"
    return (
        f"## Idea card\nTitle: {card['title']}\nChapter: {card['chapter']}\n"
        f"Question it serves: {card['question']}\n\n{card['body']}\n\n"
        f"## Evidence notes cited\n{notes}\n\n"
        f"## Original raw sources cited\n{raw}\n\n"
        f"## Voice guidelines\n{voice}\n\n"
        f"## Format rules\n{fmt}\n\n"
        f"## Lines bank\n{lines_bank}"
    )


def _page_url(page_id: str) -> str:
    return f"https://www.notion.so/{page_id.replace('-', '')}"


def run(notion: Notion, ids: dict, llm_complete=complete,
        idea_id: str | None = None, lines_dir: Path = LINES_DIR,
        feed_dir: Path = REPO_ROOT / "feed",
        manifest_file: Path | None = None) -> int:
    rows = notion.query(ids["idea_cards_db"], filter={
        "property": "Status", "select": {"equals": "chosen"}
    })
    if idea_id:
        rows = [row for row in rows if row["id"] == idea_id]
    if not rows:
        print("no chosen cards")
        return 0

    voice = "\n\n".join(
        notion.get_page_markdown(page_id)
        for name, page_id in ids["pages"].items() if name.startswith("Voice /")
    )
    lines_bank = "\n\n".join(
        path.read_text() for path in sorted(lines_dir.glob("*.md"))
    )
    prompt = PROMPT_PATH.read_text()

    for row in rows:
        card = card_from_row(row)
        card["body"] = notion.get_page_markdown(card["id"])
        fmt = notion.get_page_markdown(ids["pages"][f"Formats / {card['format']}"])
        notes_md = [notion.get_page_markdown(nid) for nid in card["sources"]]
        raw_sources = raw_sources_for_notes(
            card["sources"], feed_dir, manifest_file
        )

        draft = llm_complete(
            prompt,
            build_user_prompt(card, notes_md, raw_sources, voice, fmt, lines_bank),
        ).strip()
        if not draft:
            print(f"FAIL {card['title']}: empty draft")
            return 1

        draft_id = notion.create_page(
            {"page_id": ids["root"]},
            {"title": [{"text": {"content": f"Draft: {card['title']}"}}]},
            children=md_to_blocks(draft),
        )
        notion.update_properties(card["id"], {
            "Status": select("drafted"),
            "Review": select("pending"),
            "Draft": {"url": _page_url(draft_id)},
        })
        print(f"drafted: {card['title']} -> {draft_id}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--idea", default=None)
    args = parser.parse_args()
    ids = json.loads(IDS_PATH.read_text())
    return run(Notion(), ids, idea_id=args.idea)


if __name__ == "__main__":
    sys.exit(main())
