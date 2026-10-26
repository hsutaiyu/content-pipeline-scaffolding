"""Snapshot the source Notion databases into feed/raw/.

Sources:
- Feedback Digests DB  -> feed/raw/digests/   (biweekly)
- Case Bank DB         -> feed/raw/casebank/  (structured case rows)

Only rows not seen before are written; seen ids live in feed/raw/.state.json
(committed, so CI runs are idempotent).

Usage: uv run python -m adapters.notion_source
"""

import json
import sys
from datetime import date
from pathlib import Path

from adapters.base import write_raw
from src.notion_io import Notion

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_PATH_NAME = ".state.json"

# Notion database ids (UUID of the database, from its URL).
DIGESTS_DB = "273374da-af72-8263-bb5a-819f31e1e1d2"
# TEST copy of the Open Value Case Bank, duplicated under Content Pipeline (TEST).
CASEBANK_DB = "088374da-af72-8222-a775-010a23dcd786"


def _plain(prop: dict) -> str:
    for key in ("title", "rich_text"):
        if key in prop:
            return "".join(t.get("plain_text", "") for t in prop[key])
    return ""


def _names(prop: dict) -> list[str]:
    return [o["name"] for o in prop.get("multi_select", [])]


def _load_state(feed_dir: Path) -> dict:
    path = feed_dir / "raw" / STATE_PATH_NAME
    if path.exists():
        return json.loads(path.read_text())
    return {"digests": [], "casebank": []}


def _save_state(feed_dir: Path, state: dict) -> None:
    path = feed_dir / "raw" / STATE_PATH_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n")


def _ingest_digests(notion, feed_dir: Path, state: dict) -> None:
    for row in notion.query(DIGESTS_DB):
        if row["id"] in state["digests"]:
            continue
        props = row["properties"]
        name = _plain(props["Name"])
        period = props.get("Period", {}).get("date") or {}
        day = period.get("end") or period.get("start") or \
            date.today().isoformat()
        body = (f"# {name}\n\n**TL;DR:** {_plain(props.get('TL;DR', {}))}\n\n"
                + notion.get_page_markdown(row["id"]))
        path = write_raw(feed_dir, "digests", day, name,
                         {"source": "digest", "date": day,
                          "period_start": period.get("start", "")}, body)
        state["digests"].append(row["id"])
        print(f"ingested digest -> {path}")


def _ingest_casebank(notion, feed_dir: Path, state: dict) -> None:
    for row in notion.query(CASEBANK_DB):
        if row["id"] in state["casebank"]:
            continue
        props = row["properties"]
        case = _plain(props["Case"])
        day = date.today().isoformat()
        flags = _names(props.get("Flags", {}))
        chapters = _names(props.get("Book One chapter", {}))
        sections = []
        for label, key in (("What happened", "What happened"),
                           ("Thesis tie", "Thesis tie"),
                           ("Post angle", "Post angle"),
                           ("Caution", "Caution"),
                           ("Source", "Source")):
            value = _plain(props.get(key, {}))
            if value:
                sections.append(f"**{label}:** {value}")
        path = write_raw(feed_dir, "casebank", day, case,
                         {"source": "casebank", "date": day,
                          "area": (props.get("Area", {}).get("select") or {})
                          .get("name", ""),
                          "chapters": chapters, "flags": flags,
                          "article": props.get("Article", {}).get("url") or ""},
                         f"# {case}\n\n" + "\n\n".join(sections))
        state["casebank"].append(row["id"])
        print(f"ingested case -> {path}")


def run(notion: Notion, feed_dir: Path) -> int:
    state = _load_state(feed_dir)
    _ingest_digests(notion, feed_dir, state)
    _ingest_casebank(notion, feed_dir, state)
    _save_state(feed_dir, state)
    return 0


def main() -> int:
    return run(Notion(), REPO_ROOT / "feed")


if __name__ == "__main__":
    sys.exit(main())
