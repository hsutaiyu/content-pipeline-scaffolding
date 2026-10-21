import json

import pytest
import responses

from src.notion_io import Notion, multi_select, relation, select, text, title

BASE = "https://api.notion.com/v1"
DB = "db-123"
PAGE = "page-456"


def make():
    return Notion(token="tok")


@responses.activate
def test_create_database_shape():
    responses.post(f"{BASE}/databases", json={"id": DB}, status=200)
    props = {"Name": title("unused"), "Status": select("x")}

    db_id = make().create_database(PAGE, "Idea Cards", props)

    assert db_id == DB
    req = responses.calls[0].request
    assert req.headers["Authorization"] == "Bearer tok"
    assert req.headers["Notion-Version"] == "2022-06-28"
    body = json.loads(req.body)
    assert body["parent"] == {"page_id": PAGE}
    assert body["title"] == [{"text": {"content": "Idea Cards"}}]
    assert body["properties"]["Status"] == {"select": {"name": "x"}}


@responses.activate
def test_query_passes_filter_and_returns_rows():
    responses.post(
        f"{BASE}/databases/{DB}/query",
        json={"results": [{"id": "r1"}, {"id": "r2"}]},
        status=200,
    )
    filt = {"property": "Status", "select": {"equals": "proposed"}}

    rows = make().query(DB, filt)

    assert [r["id"] for r in rows] == ["r1", "r2"]
    assert json.loads(responses.calls[0].request.body)["filter"] == filt


@responses.activate
def test_query_paginates():
    responses.post(
        f"{BASE}/databases/{DB}/query",
        json={"results": [{"id": "r1"}], "has_more": True, "next_cursor": "c1"},
        status=200,
    )
    responses.post(
        f"{BASE}/databases/{DB}/query",
        json={"results": [{"id": "r2"}], "has_more": False},
        status=200,
    )

    rows = make().query(DB)

    assert [r["id"] for r in rows] == ["r1", "r2"]
    assert json.loads(responses.calls[1].request.body)["start_cursor"] == "c1"


@responses.activate
def test_create_and_update_page():
    responses.post(f"{BASE}/pages", json={"id": PAGE}, status=200)
    responses.patch(f"{BASE}/pages/{PAGE}", json={"id": PAGE}, status=200)
    n = make()

    page_id = n.create_page(
        {"database_id": DB},
        {"Name": title("Card"), "Beats": multi_select(["a", "b"])},
        children=[{"object": "block", "type": "paragraph",
                   "paragraph": {"rich_text": [{"text": {"content": "body"}}]}}],
    )
    n.update_properties(page_id, {"Status": select("chosen")})

    assert page_id == PAGE
    create_body = json.loads(responses.calls[0].request.body)
    assert create_body["properties"]["Beats"] == {
        "multi_select": [{"name": "a"}, {"name": "b"}]
    }
    assert len(create_body["children"]) == 1
    patch_body = json.loads(responses.calls[1].request.body)
    assert patch_body["properties"]["Status"] == {"select": {"name": "chosen"}}


@responses.activate
def test_append_blocks():
    responses.patch(f"{BASE}/blocks/{PAGE}/children", json={"results": []}, status=200)
    blocks = [{"object": "block", "type": "divider", "divider": {}}]

    make().append_blocks(PAGE, blocks)

    assert json.loads(responses.calls[0].request.body)["children"] == blocks


@responses.activate
def test_get_page_markdown():
    responses.get(
        f"{BASE}/blocks/{PAGE}/children",
        json={
            "results": [
                {"type": "heading_2", "heading_2": {
                    "rich_text": [{"plain_text": "Claims"}]}},
                {"type": "bulleted_list_item", "bulleted_list_item": {
                    "rich_text": [{"plain_text": "claim one"}]}},
                {"type": "paragraph", "paragraph": {
                    "rich_text": [{"plain_text": "a paragraph"}]}},
            ],
            "has_more": False,
        },
        status=200,
    )

    md = make().get_page_markdown(PAGE)

    assert md == "## Claims\n- claim one\na paragraph"


def test_property_helpers():
    assert text("hi") == {"rich_text": [{"text": {"content": "hi"}}]}
    assert relation(["a", "b"]) == {"relation": [{"id": "a"}, {"id": "b"}]}


@responses.activate
def test_update_database_adds_property():
    responses.patch(f"{BASE}/databases/{DB}", json={"id": DB}, status=200)

    make().update_database(DB, {"Used-by": {"relation": {"database_id": "other-db"}}})

    body = json.loads(responses.calls[0].request.body)
    assert body["properties"] == {"Used-by": {"relation": {"database_id": "other-db"}}}


@responses.activate
def test_archive_list_delete():
    responses.patch(f"{BASE}/pages/{PAGE}", json={"id": PAGE}, status=200)
    responses.get(f"{BASE}/blocks/{PAGE}/children",
                  json={"results": [{"id": "b1"}, {"id": "b2"}],
                        "has_more": False}, status=200)
    responses.delete(f"{BASE}/blocks/b1", json={}, status=200)
    n = make()

    n.archive_page(PAGE)
    assert json.loads(responses.calls[0].request.body) == {"archived": True}

    blocks = n.list_blocks(PAGE)
    assert [b["id"] for b in blocks] == ["b1", "b2"]

    n.delete_block("b1")
    assert responses.calls[2].request.method == "DELETE"


@responses.activate
def test_error_raises():
    responses.post(f"{BASE}/databases/{DB}/query", json={}, status=429)

    with pytest.raises(RuntimeError, match="429"):
        make().query(DB)
