from src.draft import build_user_prompt, card_from_row, run


def card_row(status="chosen"):
    return {
        "id": "card-1",
        "properties": {
            "Name": {"title": [{"plain_text": "The log that never judges"}]},
            "Status": {"select": {"name": status}},
            "Format": {"select": {"name": "x-post"}},
            "Chapter": {"rich_text": [{"plain_text": "4 · Show Your Work"}]},
            "Question": {"rich_text": [{"plain_text": "What already works?"}]},
            "Sources": {"relation": [{"id": "note-1"}]},
        },
    }


class FakeNotion:
    def __init__(self):
        self.created = []
        self.updated = []

    def query(self, db_id, filter=None, sorts=None):
        return [card_row()]

    def get_page_markdown(self, page_id):
        return {
            "card-1": "**Hook:** CT records without judging.",
            "note-1": "## Claims\n- CT exists since 2013",
            "voice-page": "voice rules",
            "fmt-page": "x-post rules",
        }[page_id]

    def create_page(self, parent, properties, children=None):
        self.created.append({"parent": parent, "children": children})
        return "draft-1"

    def update_properties(self, page_id, properties):
        self.updated.append((page_id, properties))


def test_card_from_row_extracts_fields():
    card = card_from_row(card_row())
    assert card["id"] == "card-1"
    assert card["title"] == "The log that never judges"
    assert card["format"] == "x-post"
    assert card["sources"] == ["note-1"]


def test_build_user_prompt_packs_everything():
    prompt = build_user_prompt(
        card={"title": "t", "chapter": "c", "question": "q",
              "body": "hook+outline"},
        notes_md=["note text"], voice="voice rules", fmt="x-post rules",
        lines_bank="line one")
    for s in ("hook+outline", "note text", "voice rules", "x-post rules",
              "line one"):
        assert s in prompt


def test_run_drafts_chosen_cards_and_updates_status(tmp_path):
    lines = tmp_path / "lines"
    lines.mkdir()
    (lines / "bank.md").write_text("line one")

    notion = FakeNotion()
    ids = {"root": "root-page", "idea_cards_db": "ideas-db",
           "pages": {"Formats / x-post": "fmt-page",
                     "Voice / heuristics": "voice-page"}}

    rc = run(notion, ids, llm_complete=lambda s, u: "a draft",
             lines_dir=lines)

    assert rc == 0
    assert len(notion.created) == 1
    assert notion.created[0]["parent"] == {"page_id": "root-page"}
    page_id, props = notion.updated[0]
    assert page_id == "card-1"
    assert props["Status"] == {"select": {"name": "drafted"}}
    assert props["Review"] == {"select": {"name": "pending"}}
    assert props["Draft"] == {"url": "https://www.notion.so/draft1"}
