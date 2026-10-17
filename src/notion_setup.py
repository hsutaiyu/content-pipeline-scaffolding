"""Provision the Notion surface: databases, seed pages, ids file.

Usage:
    1. In Notion, create one empty page (e.g. "OV Content Pipeline") and share
       it with the integration.
    2. export NOTION_API_KEY=... NOTION_ROOT_PAGE_ID=<that page's id>
    3. uv run python -m src.notion_setup

Idempotent: if notion_ids.json exists, provisioning is refused. Delete the file
to start over (existing Notion objects are not cleaned up automatically).
"""

import json
import os
import sys
from pathlib import Path

from src.notion_io import Notion

IDS_FILE = Path("notion_ids.json")

IDEA_CARDS_SCHEMA = {
    "Name": {"title": {}},
    "Status": {"select": {"options": [
        {"name": s} for s in ["proposed", "chosen", "drafted", "published",
                              "rejected"]]}},
    "Chapter": {"rich_text": {}},
    "Question": {"rich_text": {}},
    "Beats": {"multi_select": {"options": []}},
    "Format": {"select": {"options": [
        {"name": f} for f in ["x-post", "x-thread", "linkedin", "yt-short",
                              "blog"]]}},
    "Review": {"select": {"options": [{"name": "pending"}, {"name": "approved"}]}},
    "Draft": {"url": {}},
}

DISTILLED_NOTES_SCHEMA = {
    "Name": {"title": {}},
    "Source": {"select": {"options": [
        {"name": s} for s in ["dayai", "gtm", "search", "bank"]]}},
    "Date": {"date": {}},
    "Beats": {"multi_select": {"options": []}},
}

SEED_PAGES = {
    "Storybook / State": (
        "# Storybook State\n\n"
        "- Current chapter:\n- Open question:\n- Handoff question:\n"
        "- Beats in play:\n- Anchors:\n"
    ),
    "Storybook / Published Log": "# Published Log\n\nNothing published yet.\n",
}


def md_to_blocks(markdown: str) -> list[dict]:
    """Minimal markdown → Notion blocks: headings, bullets, paragraphs."""
    blocks = []
    for line in markdown.splitlines():
        line = line.rstrip()
        if not line:
            continue
        if line.startswith("### "):
            kind, content = "heading_3", line[4:]
        elif line.startswith("## "):
            kind, content = "heading_2", line[3:]
        elif line.startswith("# "):
            kind, content = "heading_1", line[2:]
        elif line.startswith("- "):
            kind, content = "bulleted_list_item", line[2:]
        else:
            kind, content = "paragraph", line
        blocks.append({"object": "block", "type": kind,
                       kind: {"rich_text": [{"text": {"content": content}}]}})
    return blocks


def _seed_page(n: Notion, root: str, title: str, markdown: str) -> str:
    return n.create_page(
        {"page_id": root},
        {"title": {"title": [{"text": {"content": title}}]}},
        children=md_to_blocks(markdown),
    )


def main() -> int:
    root = os.environ.get("NOTION_ROOT_PAGE_ID", "")
    if not root:
        print("NOTION_ROOT_PAGE_ID is required (see module docstring).")
        return 1
    if IDS_FILE.exists():
        print(f"{IDS_FILE} exists — already provisioned. Delete it to redo.")
        return 1

    n = Notion()
    ids: dict = {"root": root, "pages": {}}

    print("Creating Distilled Notes database…")
    distilled_db = n.create_database(root, "Distilled Notes", DISTILLED_NOTES_SCHEMA)
    ids["distilled_notes_db"] = distilled_db

    print("Creating Idea Cards database…")
    ideas_db = n.create_database(root, "Idea Cards", IDEA_CARDS_SCHEMA)
    ids["idea_cards_db"] = ideas_db

    print("Wiring relations…")
    n.update_database(ideas_db, {
        "Sources": {"relation": {"database_id": distilled_db}}})
    n.update_database(distilled_db, {
        "Used-by": {"relation": {"database_id": ideas_db}}})

    for page_title, markdown in SEED_PAGES.items():
        print(f"Seeding {page_title}…")
        ids["pages"][page_title] = _seed_page(n, root, page_title, markdown)

    for fmt_path in sorted(Path("formats").glob("*.md")):
        page_title = f"Formats / {fmt_path.stem}"
        print(f"Seeding {page_title}…")
        ids["pages"][page_title] = _seed_page(
            n, root, page_title, fmt_path.read_text())

    voice = Path("voice/guidelines.md")
    if voice.exists():
        print("Seeding Voice / Guidelines…")
        ids["pages"]["Voice / Guidelines"] = _seed_page(
            n, root, "Voice / Guidelines", voice.read_text())

    IDS_FILE.write_text(json.dumps(ids, indent=2) + "\n")

    print(f"\nDone. Ids written to {IDS_FILE} (gitignored).")
    print("\nManual step — create the two gate views on the Idea Cards database:")
    print('  1. "Ideas awaiting selection": filter Status = proposed')
    print('  2. "Drafts awaiting approval": filter Status = drafted AND'
          " Review = pending")
    print("Bookmark both view URLs; they are the team's interface.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
