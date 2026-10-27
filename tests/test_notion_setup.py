from src.notion_setup import (
    EVIDENCE_NOTES_SCHEMA,
    IDEA_CARDS_SCHEMA,
    md_to_blocks,
)


def _options(schema, prop):
    return {o["name"] for o in schema[prop]["select"]["options"]}


def test_idea_cards_schema_matches_spec():
    s = IDEA_CARDS_SCHEMA
    assert s["Name"] == {"title": {}}
    assert _options(s, "Status") == {
        "proposed", "chosen", "drafted", "published", "rejected"
    }
    assert _options(s, "Format") == {
        "x-post", "x-thread", "linkedin", "yt-short", "blog"
    }
    assert _options(s, "Review") == {"pending", "approved"}
    assert s["Chapter"] == {"rich_text": {}}
    assert s["Question"] == {"rich_text": {}}
    assert s["Beats"] == {"multi_select": {"options": []}}
    assert s["Draft"] == {"url": {}}
    # Sources relation is wired after both DBs exist (needs the target id).
    assert "Sources" not in s


def test_evidence_notes_schema_matches_spec():
    s = EVIDENCE_NOTES_SCHEMA
    assert s["Name"] == {"title": {}}
    assert _options(s, "Source") == {"digest", "casebank", "search"}
    assert s["Date"] == {"date": {}}
    assert s["Beats"] == {"multi_select": {"options": []}}
    # Used-by relation is wired after both DBs exist.
    assert "Used-by" not in s


def test_md_to_blocks():
    blocks = md_to_blocks("# Title\n\n- one\n- two\n\nplain line\n")
    kinds = [b["type"] for b in blocks]
    assert kinds == ["heading_1", "bulleted_list_item", "bulleted_list_item",
                     "paragraph"]
    assert blocks[0]["heading_1"]["rich_text"][0]["text"]["content"] == "Title"
    assert blocks[3]["paragraph"]["rich_text"][0]["text"]["content"] == "plain line"
