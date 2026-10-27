import pytest

from src.evidence import (
    evidence_db_id,
    manifest_path,
    raw_sources_for_notes,
)


def test_evidence_db_id_accepts_current_and_legacy_keys():
    assert evidence_db_id({"evidence_notes_db": "new"}) == "new"
    assert evidence_db_id({"distilled_notes_db": "old"}) == "old"


def test_manifest_path_preserves_existing_legacy_file(tmp_path):
    legacy = tmp_path / "distilled-manifest.json"
    legacy.write_text("{}")
    assert manifest_path(tmp_path) == legacy
    (tmp_path / "evidence-manifest.json").write_text("{}")
    assert manifest_path(tmp_path) == tmp_path / "evidence-manifest.json"


def test_raw_sources_include_front_matter_and_are_deduplicated(tmp_path):
    feed = tmp_path / "feed"
    case = feed / "raw" / "casebank" / "case.md"
    case.parent.mkdir(parents=True)
    case.write_text("---\nflags:\n- Strong pick\n---\n\nCase body\n")
    digest = feed / "raw" / "digest" / "digest.md"
    digest.parent.mkdir(parents=True)
    digest.write_text("digest body")
    (feed / "distilled-manifest.json").write_text(
        '{"casebank/case.md": "note-1", '
        '"digest/digest.md": ["note-2", "note-3"]}'
    )

    sources = raw_sources_for_notes(["note-1", "note-2", "note-3"], feed)

    assert len(sources) == 2
    assert "Strong pick" in sources[0]["text"]
    assert sources[1]["note_ids"] == ["note-2", "note-3"]


def test_missing_raw_mapping_fails_loudly(tmp_path):
    with pytest.raises(RuntimeError, match="note-missing"):
        raw_sources_for_notes(["note-missing"], tmp_path / "feed")
