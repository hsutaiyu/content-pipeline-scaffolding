import json

from src.ideate import build_user_prompt, parse_cards, render_card_body, run

CARDS_JSON = json.dumps([{
    "title": "The log that never judges",
    "hook": "Certificate Transparency has recorded every TLS certificate since 2013 without deciding which should exist.",
    "outline": ["CT as working precedent", "record without judgement",
                    "what this means for value"],
    "chapter": "4 · Show Your Work",
    "question": "What already works that we can build on?",
    "beats": ["4 · Show Your Work"],
    "format": "x-post",
    "source_note_ids": ["note-1"],
}])


class FakeNotion:
    def __init__(self):
        self.created = []
        self.appended = []

    def get_page_markdown(self, page_id):
        return {"state-page": "current chapter state",
                "log-page": "published log"}.get(page_id, f"md for {page_id}")

    def query(self, db_id, filter=None, sorts=None):
        if db_id == "distilled-db":
            return [{"id": "note-1", "properties": {
                "Name": {"title": [{"plain_text": "digest · 2026-10-19"}]}}}]
        return []  # existing idea cards: none

    def create_page(self, parent, properties, children=None):
        self.created.append({"parent": parent, "properties": properties,
                             "children": children})
        return "card-1"

    def append_blocks(self, page_id, blocks):
        self.appended.append((page_id, blocks))


def test_parse_cards_tolerates_fences():
    cards = parse_cards(f"```json\n{CARDS_JSON}\n```")
    assert cards[0]["title"] == "The log that never judges"


def test_render_card_body_has_hook_and_outline():
    body = render_card_body(parse_cards(CARDS_JSON)[0])
    assert body.startswith("**Hook:**")
    assert "- CT as working precedent" in body


def test_build_user_prompt_includes_state_and_notes():
    prompt = build_user_prompt(
        state="STATE", published_log="LOG",
        notes=[{"id": "note-1", "title": "n1", "markdown": "claims here"}],
        existing_titles=["old idea"])
    assert "STATE" in prompt and "LOG" in prompt
    assert "claims here" in prompt and "old idea" in prompt
    assert "note-1" in prompt


def test_run_creates_proposed_cards_with_relations():
    notion = FakeNotion()
    ids = {"idea_cards_db": "ideas-db", "distilled_notes_db": "distilled-db",
           "pages": {"Storybook / State": "state-page",
                     "Storybook / Published Log": "log-page"}}

    rc = run(notion, ids, llm_complete=lambda s, u: CARDS_JSON)

    assert rc == 0
    assert len(notion.created) == 1
    card = notion.created[0]
    assert card["parent"] == {"database_id": "ideas-db"}
    props = card["properties"]
    assert props["Status"] == {"select": {"name": "proposed"}}
    assert props["Review"] == {"select": {"name": "pending"}}
    assert props["Sources"] == {"relation": [{"id": "note-1"}]}
    assert props["Format"] == {"select": {"name": "x-post"}}
    assert card["children"]  # hook + outline blocks
    # run summary appended to the state page
    assert notion.appended[0][0] == "state-page"
