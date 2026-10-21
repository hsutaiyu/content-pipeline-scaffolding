import json

from adapters.notion_source import CASEBANK_DB, DIGESTS_DB, run


def digest_row(rid="row-1"):
    return {"id": rid, "properties": {
        "Name": {"title": [{"plain_text": "Digest — Oct 6–19, 2026"}]},
        "Period": {"date": {"start": "2026-10-06", "end": "2026-10-19"}},
        "TL;DR": {"rich_text": [{"plain_text": "3 calls."}]},
    }}


def case_row(rid="case-1"):
    return {"id": rid, "properties": {
        "Case": {"title": [{"plain_text": "Certificate Transparency"}]},
        "Ref": {"rich_text": [{"plain_text": "Registries 01"}]},
        "Area": {"select": {"name": "Registries and identity"}},
        "Book One chapter": {"multi_select": [{"name": "3 · What Would Have to Be True"}]},
        "Flags": {"multi_select": [{"name": "Strong pick"}]},
        "Article": {"url": "https://www.rfc-editor.org/rfc/rfc9162.html"},
        "What happened": {"rich_text": [{"plain_text": "Append-only logs since 2013."}]},
        "Thesis tie": {"rich_text": [{"plain_text": "Record without judgement."}]},
        "Post angle": {"rich_text": [{"plain_text": "Browsers decide, logs record."}]},
        "Caution": {"rich_text": [{"plain_text": "Not news; frame as precedent."}]},
        "Source": {"rich_text": [{"plain_text": "RFC 9162, IETF"}]},
    }}


class FakeNotion:
    def query(self, db_id, filter=None, sorts=None):
        return {DIGESTS_DB: [digest_row()], CASEBANK_DB: [case_row()]}[db_id]

    def get_page_markdown(self, page_id):
        return f"full content of {page_id}"


def test_ingest_writes_dated_files(tmp_path):
    rc = run(FakeNotion(), tmp_path)
    assert rc == 0

    digest = (tmp_path / "raw" / "digests").glob("*.md")
    digest = list(digest)
    assert len(digest) == 1
    assert digest[0].name.startswith("2026-10-19-")
    text = digest[0].read_text()
    assert "source: digest" in text
    assert "full content of row-1" in text

    case = list((tmp_path / "raw" / "casebank").glob("*.md"))
    assert len(case) == 1
    text = case[0].read_text()
    assert "source: casebank" in text
    assert "Strong pick" in text
    assert "Record without judgement." in text


def test_ingest_skips_seen_rows(tmp_path):
    notion = FakeNotion()
    run(notion, tmp_path)
    state = json.loads((tmp_path / "raw" / ".state.json").read_text())
    assert state["digests"] == ["row-1"]
    assert state["casebank"] == ["case-1"]

    run(notion, tmp_path)  # second run: nothing new
    assert len(list((tmp_path / "raw" / "digests").glob("*.md"))) == 1
    assert len(list((tmp_path / "raw" / "casebank").glob("*.md"))) == 1
