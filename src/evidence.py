"""Shared evidence-store helpers and raw-source resolution."""

import json
from pathlib import Path

MANIFEST_NAME = "evidence-manifest.json"
LEGACY_MANIFEST_NAME = "distilled-manifest.json"


def evidence_db_id(ids: dict) -> str:
    """Read the current id key while accepting pre-rename installations."""
    return ids.get("evidence_notes_db") or ids["distilled_notes_db"]


def manifest_path(feed_dir: Path) -> Path:
    """Prefer the current name, but keep using an existing legacy manifest."""
    current = feed_dir / MANIFEST_NAME
    legacy = feed_dir / LEGACY_MANIFEST_NAME
    return legacy if legacy.exists() and not current.exists() else current


def load_manifest(path: Path) -> dict[str, list[str] | str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"Evidence manifest must be a JSON object: {path}")
    return data


def save_manifest(path: Path, manifest: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(manifest, indent=2) + "\n")
    tmp.replace(path)


def _page_ids(value: list[str] | str) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(i, str) for i in value):
        return value
    raise ValueError("Manifest values must be a page id or a list of page ids")


def raw_sources_for_notes(note_ids: list[str], feed_dir: Path,
                          manifest_file: Path | None = None) -> list[dict]:
    """Return each cited raw file once, retaining its relationship to notes.

    Raw text includes front matter: flags, curated chapters, and article URLs
    are part of the evidence contract and must reach downstream agents.
    """
    path = manifest_file or manifest_path(feed_dir)
    by_note = {
        page_id: rel
        for rel, value in load_manifest(path).items()
        for page_id in _page_ids(value)
    }
    missing = [nid for nid in note_ids if nid not in by_note]
    if missing:
        raise RuntimeError(
            "No raw-source mapping for evidence note(s): " + ", ".join(missing)
            + f". Repair or regenerate {path} before continuing."
        )

    raw_root = (feed_dir / "raw").resolve()
    sources: list[dict] = []
    by_path: dict[str, dict] = {}
    for note_id in note_ids:
        rel = by_note[note_id]
        raw_file = (raw_root / rel).resolve()
        if raw_root != raw_file and raw_root not in raw_file.parents:
            raise RuntimeError(f"Raw source escapes feed/raw: {rel}")
        if not raw_file.is_file():
            raise RuntimeError(f"Raw source is missing: {raw_file}")
        if rel not in by_path:
            source = {"path": rel, "text": raw_file.read_text(), "note_ids": []}
            by_path[rel] = source
            sources.append(source)
        by_path[rel]["note_ids"].append(note_id)
    return sources
