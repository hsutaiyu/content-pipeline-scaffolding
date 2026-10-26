import json

from src.ideate import (
    build_user_prompt,
    current_chapter,
    parse_cards,
    render_card_body,
    run,
)

STATE = """# Storybook State
- **Current chapter:** 4 · Show Your Work (Oct 20–26) — Part One
- **Open question:** What already works?
"""

CARDS_JSON = json.dumps([{
    "title": "The log that never judges",
    "hook": "Certificate Transparency records certificates without judging them.",
    "central_tension": "A shared record can support different trust decisions.",
    "arc_fit": "CT is a working precedent for the chapter's question.",
    "outline": ["CT as precedent", "record without judgement",
                "what this means for value"],
    "chapter": "4 · Show Your Work",
    "question": "What already works that we can build on?",
    "beats": ["4 · Show Your Work"],
    "format": "x-post",
    "source_note_ids": ["note-1"],
    "cautions": ["Frame CT as a precedent, not news."],
}])


def note_row(note_id, chapter):
    return {"id": note_id, "properties": {
        "Name": {"title": [{"plain_text": f"title-{note_id}"}]},
        "Beats": {"multi_select": [{"name": chapter}]},
        "Source": {"select": {"name": "casebank"}},
        "Date": {"date": {"start": "2026-10-19"}},
    }}


class FakeNotion:
    def __init__(self):
        self.created = []
        self.appended = []
        self.requested = []

    def get_page_markdown(self, page_id):
        self.requested.append(page_id)
        return {
            "state-page": STATE,
            "log-page": "published log",
            "note-1": "evidence one",
            "note-2": "evidence two",
        }[page_id]

    def query(self, db_id, filter=None, sorts=None):
        if db_id == "evidence-db":
            return [note_row("note-1", "4 · Show Your Work"),
                    note_row("note-2", "5 · Who's Really There?")]
        return []

    def create_page(self, parent, properties, children=None):
        self.created.append({"parent": parent, "properties": properties,
                             "children": children})
        return "card-1"

    def append_blocks(self, page_id, blocks):
        self.appended.append((page_id, blocks))


def test_parse_cards_tolerates_fences():
    cards = parse_cards(f"```json\n{CARDS_JSON}\n```")
    assert cards[0]["title"] == "The log that never judges"


def test_render_card_body_preserves_tension_arc_and_cautions():
    body = render_card_body(parse_cards(CARDS_JSON)[0])
    assert body.startswith("**Hook:**")
    assert "Central tension" in body
    assert "Why it serves the chapter" in body
    assert "Frame CT as a precedent, not news." in body


def test_build_user_prompt_includes_metadata_notes_and_raw_sources():
    prompt = build_user_prompt(
        state="STATE", published_log="LOG",
        notes=[{
            "id": "note-1", "title": "n1", "markdown": "claims here",
            "source": "casebank", "date": "2026-10-19",
            "beats": ["4 · Show Your Work"], "raw_paths": ["casebank/x.md"],
        }],
        existing_titles=["old idea"],
        raw_sources=[{"path": "casebank/x.md", "text": "RAW CAUTION",
                      "note_ids": ["note-1"]}],
    )
    for expected in (
        "STATE", "LOG", "claims here", "old idea", "note-1",
        "casebank", "4 · Show Your Work", "RAW CAUTION",
    ):
        assert expected in prompt


def test_current_chapter_drops_date_and_part_suffix():
    assert current_chapter(STATE) == "4 · Show Your Work"
    assert current_chapter("- Current chapter: 4 · Show Your Work (Oct 20–26)") == \
        "4 · Show Your Work"


def test_run_filters_by_chapter_and_loads_only_selected_raw_sources(tmp_path):
    feed = tmp_path / "feed"
    raw = feed / "raw" / "casebank" / "one.md"
    raw.parent.mkdir(parents=True)
    raw.write_text("---\nflags:\n- Strong pick\n---\n\nFull raw case")
    (feed / "evidence-manifest.json").write_text(json.dumps({
        "casebank/one.md": ["note-1"],
        "casebank/two.md": ["note-2"],
    }))
    notion = FakeNotion()
    ids = {"idea_cards_db": "ideas-db", "evidence_notes_db": "evidence-db",
           "pages": {"Storybook / State": "state-page",
                     "Storybook / Published Log": "log-page"}}
    prompts = []

    def fake_llm(system, user):
        prompts.append(user)
        return CARDS_JSON

    rc = run(notion, ids, llm_complete=fake_llm, feed_dir=feed)

    assert rc == 0
    assert "note-1" in notion.requested
    assert "note-2" not in notion.requested
    assert "Full raw case" in prompts[0]
    assert "evidence two" not in prompts[0]
    card = notion.created[0]
    assert card["parent"] == {"database_id": "ideas-db"}
    props = card["properties"]
    assert props["Status"] == {"select": {"name": "proposed"}}
    assert props["Sources"] == {"relation": [{"id": "note-1"}]}
    assert card["children"]
    assert notion.appended[0][0] == "state-page"
