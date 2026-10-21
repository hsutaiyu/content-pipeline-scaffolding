import json

import pytest

from src.reset import run


class FakeNotion:
    def __init__(self):
        self.archived = []
        self.deleted = []
        self.appended = []

    def query(self, db_id, filter=None, sorts=None):
        return [{"id": f"{db_id}-row-1"}]

    def list_blocks(self, page_id):
        if page_id == "root-page":
            return [{"id": "b-draft", "type": "child_page",
                     "child_page": {"title": "Draft: something"}},
                    {"id": "b-db", "type": "child_database",
                     "child_database": {"title": "Idea Cards"}}]
        return [{"id": f"{page_id}-block-1", "type": "paragraph",
                 "paragraph": {"rich_text": []}}]

    def archive_page(self, page_id):
        self.archived.append(page_id)

    def delete_block(self, block_id):
        self.deleted.append(block_id)

    def append_blocks(self, page_id, blocks):
        self.appended.append((page_id, blocks))


IDS = {"root": "root-page", "idea_cards_db": "ideas", "distilled_notes_db": "distilled",
       "pages": {"Storybook / State": "state-page",
                 "Storybook / Published Log": "log-page"}}


@pytest.fixture
def feed(tmp_path):
    raw = tmp_path / "feed" / "raw" / "digests"
    raw.mkdir(parents=True)
    (raw / "2026-10-19-x.md").write_text("raw")
    (tmp_path / "feed" / "distilled-manifest.json").write_text("{}")
    (tmp_path / "feed" / "raw" / ".state.json").write_text("{}")
    return tmp_path / "feed"


def test_requires_confirmation(feed):
    notion = FakeNotion()
    with pytest.raises(SystemExit):
        run(notion, IDS, feed, confirm="wrong")
    assert notion.archived == []


def test_reset_archives_wipes_reseeds(feed, tmp_path):
    notion = FakeNotion()
    state_seed = tmp_path / "storybook" / "state.md"
    state_seed.parent.mkdir()
    state_seed.write_text("# fresh state")

    run(notion, IDS, feed, confirm="reset", storybook_seed=state_seed)

    # every row in both DBs archived, draft page archived, DB itself untouched
    assert set(notion.archived) == {"ideas-row-1", "distilled-row-1", "b-draft"}
    # state + log pages wiped
    assert "state-page-block-1" in notion.deleted
    assert "log-page-block-1" in notion.deleted
    # both re-seeded
    seeded = {pid for pid, _ in notion.appended}
    assert seeded == {"state-page", "log-page"}
    # feed cleaned
    assert not list((feed / "raw").rglob("*.md"))
    assert not (feed / "distilled-manifest.json").exists()
    assert not (feed / "raw" / ".state.json").exists()
