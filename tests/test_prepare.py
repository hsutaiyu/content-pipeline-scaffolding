import json

from src.prepare import (
    parse_raw,
    render_casebank_note,
    run,
    storybook_chapters,
)

STATE = """# Storybook State

| Dates | Chapter | Hands off |
|---|---|---|
| Oct 20–26 | 4 · Show Your Work | Across many? |
| Oct 27–Nov 2 | 5 · Who's Really There? | What happened? |
"""

DIGEST_JSON = json.dumps([{
    "theme": "Tokenless incentives",
    "claims": ["Six callers raised incentives independently."],
    "objections": ["Infrastructure still has to be paid for."],
    "open_questions": ["Who pays maintainers?"],
    "tensions": ["No token does not mean no economic incentive."],
    "examples": ["Social reputation was proposed."],
    "quotes": [{"text": "the users would have to pay", "speaker": "Edith"}],
    "numbers": ["About six calls, independently reported."],
    "cautions": ["The calls were exploratory."],
    "why_it_matters": "The service needs a workable participation model.",
    "beats": ["4 · Show Your Work"],
}, {
    "theme": "Proof compactness",
    "beats": ["5 · Who's Really There?"],
}])


class FakeNotion:
    def __init__(self):
        self.created = []
        self.appended = []

    def create_page(self, parent, properties, children=None):
        self.created.append({"parent": parent, "properties": properties})
        return f"page-{len(self.created)}"

    def append_blocks(self, page_id, blocks):
        self.appended.append((page_id, blocks))


def write_raw(tmp_path, source="casebank", name="2026-10-19-input.md",
              body="# Input\n", extra=""):
    directory = tmp_path / "feed" / "raw" / source
    directory.mkdir(parents=True)
    path = directory / name
    path.write_text(
        f"---\nsource: {source}\ndate: 2026-10-19\n{extra}\n---\n\n{body}"
    )
    return path


def block_text(notion):
    lines = []
    for _, blocks in notion.appended:
        for block in blocks:
            kind = block["type"]
            lines.append(block[kind]["rich_text"][0]["text"]["content"])
    return "\n".join(lines)


def test_parse_raw_front_matter(tmp_path):
    path = write_raw(tmp_path, source="digest", body="# Digest\n\nSome notes.")
    meta, body = parse_raw(path)
    assert meta["source"] == "digest"
    assert str(meta["date"]) == "2026-10-19"
    assert "Some notes." in body


def test_storybook_chapters_come_from_whole_arc():
    assert storybook_chapters(STATE) == [
        "4 · Show Your Work", "5 · Who's Really There?"
    ]


def test_casebank_is_copied_deterministically_without_llm(tmp_path):
    body = """# Certificate Transparency

**What happened:** Append-only logs record certificates.

**Thesis tie:** Record without judgement.

**Post angle:** Browsers decide; logs record.

**Caution:** Not news; frame as precedent.

**Source:** RFC 9162, IETF
"""
    write_raw(tmp_path, body=body, extra="""chapters:
- 4 · Show Your Work
flags:
- Strong pick
article: https://www.rfc-editor.org/rfc/rfc9162.html""")

    def no_llm(*args):
        raise AssertionError("Case Bank must not call the LLM")

    notion = FakeNotion()
    manifest = tmp_path / "feed" / "evidence-manifest.json"
    rc = run(tmp_path / "feed", manifest, notion, llm_complete=no_llm,
             storybook_state=STATE, evidence_notes_db_id="db-x")

    assert rc == 0
    assert len(notion.created) == 1
    props = notion.created[0]["properties"]
    assert props["Beats"] == {
        "multi_select": [{"name": "4 · Show Your Work"}]
    }
    text = block_text(notion)
    for expected in (
        "Raw path: feed/raw/casebank/2026-10-19-input.md",
        "Strong pick", "https://www.rfc-editor.org/rfc/rfc9162.html",
        "Browsers decide; logs record.", "Not news; frame as precedent.",
        "RFC 9162, IETF",
    ):
        assert expected in text
    assert json.loads(manifest.read_text()) == {
        "casebank/2026-10-19-input.md": ["page-1"]
    }

    # A second run skips the prepared raw item and still makes no LLM call.
    assert run(tmp_path / "feed", manifest, notion, llm_complete=no_llm,
               storybook_state=STATE, evidence_notes_db_id="db-x") == 0
    assert len(notion.created) == 1


def test_casebank_renderer_preserves_unstructured_input():
    markdown = render_casebank_note({}, "unstructured source", "casebank/x.md")
    assert "## Source material\nunstructured source" in markdown


def test_digest_becomes_theme_packets_with_full_front_matter(tmp_path):
    write_raw(tmp_path, source="digest", name="2026-10-19-digest.md",
              body="# Digest\n\nSix callers discussed incentives: "
                   "\"the users would have to pay\".",
              extra="period_start: '2026-10-06'")
    notion = FakeNotion()
    manifest = tmp_path / "feed" / "evidence-manifest.json"
    prompts = []

    def fake_llm(system, user):
        prompts.append(user)
        return DIGEST_JSON

    rc = run(tmp_path / "feed", manifest, notion, llm_complete=fake_llm,
             storybook_state=STATE, evidence_notes_db_id="db-x")

    assert rc == 0
    assert len(notion.created) == 2
    first_title = notion.created[0]["properties"]["Name"]["title"][0]
    assert "Tokenless incentives" in first_title["text"]["content"]
    assert "period_start: '2026-10-06'" in prompts[0]
    assert "Six callers discussed incentives:" in prompts[0]
    text = block_text(notion)
    for expected in (
        "Objections", "Who pays maintainers?", "Tensions",
        "the users would have to pay — Edith", "The calls were exploratory.",
        "Period start: 2026-10-06",
    ):
        assert expected in text
    assert json.loads(manifest.read_text()) == {
        "digest/2026-10-19-digest.md": ["page-1", "page-2"]
    }


def test_digest_rejects_invalid_chapter_before_writing(tmp_path):
    write_raw(tmp_path, source="digest", name="2026-10-19-digest.md")
    notion = FakeNotion()
    manifest = tmp_path / "feed" / "evidence-manifest.json"
    invalid = json.dumps([{"theme": "x", "beats": ["Show Your Work"]}])

    rc = run(tmp_path / "feed", manifest, notion,
             llm_complete=lambda s, u: invalid, storybook_state=STATE,
             evidence_notes_db_id="db-x")

    assert rc == 1
    assert notion.created == []
    assert not manifest.exists()


def test_digest_rejects_nonverbatim_quote_before_writing(tmp_path):
    write_raw(tmp_path, source="digest", name="2026-10-19-digest.md",
              body="original wording")
    notion = FakeNotion()
    manifest = tmp_path / "feed" / "evidence-manifest.json"
    invalid = json.dumps([{
        "theme": "x",
        "quotes": [{"text": "paraphrased wording", "speaker": "Someone"}],
    }])

    rc = run(tmp_path / "feed", manifest, notion,
             llm_complete=lambda s, u: invalid, storybook_state=STATE,
             evidence_notes_db_id="db-x")

    assert rc == 1
    assert notion.created == []
    assert not manifest.exists()


def test_digest_recovers_from_invalid_chapters_with_feedback(tmp_path):
    write_raw(tmp_path, source="digest", name="2026-10-19-digest.md",
              body="Six callers discussed incentives: the users would have to pay.\n")
    notion = FakeNotion()
    manifest = tmp_path / "feed" / "evidence-manifest.json"
    invalid = json.dumps([{"theme": "x", "beats": ["Show Your Work"]}])
    calls = []

    def flaky_llm(system, user):
        calls.append(user)
        return invalid if len(calls) == 1 else DIGEST_JSON

    rc = run(tmp_path / "feed", manifest, notion,
             llm_complete=flaky_llm, storybook_state=STATE,
             evidence_notes_db_id="db-x")

    assert rc == 0
    assert len(calls) == 2
    assert "previous extraction was rejected" in calls[1]
    assert "Show Your Work" in calls[1]
    assert len(notion.created) == 2


def test_digest_rejects_bad_json_before_writing(tmp_path):
    write_raw(tmp_path, source="digest", name="2026-10-19-digest.md")
    notion = FakeNotion()
    manifest = tmp_path / "feed" / "evidence-manifest.json"

    rc = run(tmp_path / "feed", manifest, notion,
             llm_complete=lambda s, u: "not json", storybook_state=STATE,
             evidence_notes_db_id="db-x")

    assert rc == 1
    assert notion.created == []
    assert not manifest.exists()
