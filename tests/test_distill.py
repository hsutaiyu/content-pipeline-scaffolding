import json

from src.distill import parse_raw, render_note_markdown, run


class FakeNotion:
    def __init__(self):
        self.created = []

    def create_page(self, parent, properties, children=None):
        self.created.append({"parent": parent, "properties": properties})
        return "page-1"

    def append_blocks(self, page_id, blocks):
        pass


def write_raw(tmp_path, source="digest", name="2026-10-19-digest.md",
              body="# Digest\n\nSome call notes."):
    d = tmp_path / "feed" / "raw" / source
    d.mkdir(parents=True)
    f = d / name
    f.write_text(f"---\nsource: {source}\ndate: 2026-10-19\n---\n\n{body}")
    return f


DISTILL_JSON = json.dumps({
    "claims": ["claim one"],
    "case_studies": ["a case"],
    "quotable_lines": ["a line"],
    "why_it_matters": "because",
    "beats": ["4 · Show Your Work"],
})


def test_parse_raw_front_matter(tmp_path):
    f = write_raw(tmp_path)
    meta, body = parse_raw(f)
    assert meta["source"] == "digest"
    assert str(meta["date"]) == "2026-10-19"
    assert "Some call notes." in body


def test_render_note_markdown():
    md = render_note_markdown(json.loads(DISTILL_JSON))
    assert "## Claims" in md
    assert "- claim one" in md
    assert "## Why it matters" in md
    assert "because" in md


def test_run_distills_new_files_and_skips_seen(tmp_path):
    write_raw(tmp_path)
    notion = FakeNotion()
    manifest = tmp_path / "feed" / "distilled-manifest.json"

    rc = run(tmp_path / "feed", manifest, notion,
             llm_complete=lambda s, u: DISTILL_JSON, storybook_state="state",
             distilled_db_id="db-x")

    assert rc == 0
    assert len(notion.created) == 1
    props = notion.created[0]["properties"]
    assert props["Source"] == {"select": {"name": "digest"}}
    assert props["Date"] == {"date": {"start": "2026-10-19"}}
    assert props["Beats"] == {"multi_select": [{"name": "4 · Show Your Work"}]}
    saved = json.loads(manifest.read_text())
    assert "digest/2026-10-19-digest.md" in saved

    # second run: nothing new to do
    rc = run(tmp_path / "feed", manifest, notion,
             llm_complete=lambda s, u: DISTILL_JSON, storybook_state="state",
             distilled_db_id="db-x")
    assert rc == 0
    assert len(notion.created) == 1


def test_run_fails_loudly_on_bad_json(tmp_path):
    write_raw(tmp_path)
    notion = FakeNotion()
    manifest = tmp_path / "feed" / "distilled-manifest.json"

    rc = run(tmp_path / "feed", manifest, notion,
             llm_complete=lambda s, u: "not json", storybook_state="state",
             distilled_db_id="db-x")

    assert rc == 1
    assert notion.created == []
    assert not manifest.exists() or "digest/2026-10-19-digest.md" not in \
        json.loads(manifest.read_text() or "{}")
