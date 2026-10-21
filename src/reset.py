"""Reset the pipeline to a clean slate.

Archives every Distilled Notes and Idea Cards row and every draft page
(soft delete — recoverable in Notion), wipes and re-seeds the Storybook /
State and Storybook / Published Log pages, and clears the local feed state.

Usage: uv run python -m src.reset --confirm reset
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

from src.notion_io import Notion
from src.notion_setup import md_to_blocks

REPO_ROOT = Path(__file__).resolve().parent.parent
IDS_PATH = REPO_ROOT / "notion_ids.json"
STORYBOOK_SEED = REPO_ROOT / "storybook" / "state.md"
EMPTY_LOG = "# Published Log\n\nNothing published yet.\n"


def run(notion: Notion, ids: dict, feed_dir: Path, confirm: str,
        storybook_seed: Path = STORYBOOK_SEED) -> int:
    if confirm != "reset":
        print("refusing to run: pass --confirm reset")
        sys.exit(2)

    for db_key in ("distilled_notes_db", "idea_cards_db"):
        for row in notion.query(ids[db_key]):
            notion.archive_page(row["id"])
            print(f"archived row {row['id']}")

    for block in notion.list_blocks(ids["root"]):
        if block.get("type") == "child_page" and \
                block["child_page"].get("title", "").startswith("Draft:"):
            notion.archive_page(block["id"])
            print(f"archived draft {block['id']}")

    for page_name, seed in (
            ("Storybook / State", storybook_seed.read_text()),
            ("Storybook / Published Log", EMPTY_LOG)):
        page_id = ids["pages"][page_name]
        for block in notion.list_blocks(page_id):
            notion.delete_block(block["id"])
        notion.append_blocks(page_id, md_to_blocks(seed))
        print(f"re-seeded {page_name}")

    manifest = feed_dir / "distilled-manifest.json"
    manifest.unlink(missing_ok=True)
    (feed_dir / "raw" / ".state.json").unlink(missing_ok=True)
    for source_dir in (feed_dir / "raw").iterdir() if \
            (feed_dir / "raw").exists() else []:
        if source_dir.is_dir():
            shutil.rmtree(source_dir)
            source_dir.mkdir()
    print("feed cleared")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", required=True)
    args = parser.parse_args()
    ids = json.loads(IDS_PATH.read_text())
    return run(Notion(), ids, REPO_ROOT / "feed", confirm=args.confirm)


if __name__ == "__main__":
    sys.exit(main())
