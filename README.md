# OV Content Pipeline

Two-agent content pipeline: immutable raw sources → reversible evidence notes →
idea cards → drafts, with human gates for idea selection and draft approval.

- **Creative agents:** ideator and drafter
- **Source preparation:** deterministic Case Bank copying plus structured LLM
  extraction for digests; this is preprocessing, not a third creative agent
- **State + human surface:** Notion (two databases, filtered views for the gates)
- **Code, prompts, raw corpus, raw-source manifest:** this repo
- **Runtime:** GitHub Actions

The pipeline is a state machine: transitions fire only on a cron tick or a
button press. Evidence summaries are retrieval aids, never replacements for the
original source. Both agents can resolve cited notes back to complete raw files.
See SPEC.md for the design.

## Evidence model

- Raw files under `feed/raw/` are immutable and include all front matter:
  curated chapters, flags, cautions, and article URLs.
- Case Bank entries are already curated, so preparation copies them into
  Evidence Notes without an LLM rewrite.
- Digest preparation extracts arc-neutral theme packets: claims, objections,
  open questions, tensions, examples, attributed quotes, numbers with
  conditions, and cautions.
- `feed/evidence-manifest.json` maps each raw file to its Evidence Note IDs.
  Legacy `distilled-manifest.json` files remain readable for compatibility.
- The ideator shortlists notes for the current chapter and reads their raw
  sources. The drafter reads only the raw sources cited by the chosen card.
  Missing raw mappings fail loudly rather than allowing lossy drafting.

## Setup

1. Create a Notion integration; share the pipeline root page and the two source
   databases with it.
2. Repo secrets: `NOTION_API_KEY`, `NOTION_ROOT_PAGE_ID`, `LLM_BASE_URL`,
   `LLM_API_KEY`, `LLM_MODEL`.
3. Run the **init** workflow (Actions → init → Run workflow). It provisions the
   Notion databases and pages, ingests the sources, and prepares evidence.
4. In Notion, add two filtered views on Idea Cards: `status = proposed`
   ("Ideas awaiting selection") and `status = drafted AND review = pending`
   ("Drafts awaiting approval"). Bookmark both — they are the team's interface.

## Buttons (Actions → workflow → Run workflow)

| Button | Does |
|---|---|
| **init** | Provision Notion → ingest → prepare evidence. Zero to ready. |
| **prepare** | Prepare new raw files; optional `limit` bounds raw items per run. |
| **ideate** | Generate idea cards (`proposed`) from current-chapter evidence and raw sources. |
| **draft** | Draft all `chosen` cards, or one card via the `idea_id` input. |
| **reset** | Archive all state and re-seed. Requires typing `reset`. |

## Gates (Notion, no terminal)

- **Idea selection:** open *Ideas awaiting selection*, set `status` to `chosen`
  or `rejected`.
- **Draft approval:** open *Drafts awaiting approval*, edit, set `review` to
  `approved`.

## Development

```bash
uv sync --group dev
uv run pytest
```

Stages run locally with the same entry points as CI:

```bash
uv run python -m src.prepare
uv run python -m src.ideate
uv run python -m src.draft
```

`notion_ids.json` must exist (created by init). New installations use
`evidence_notes_db`; legacy `distilled_notes_db` IDs are accepted during
migration. Regenerate old evidence notes and their manifest before running
either agent so every cited note has a raw-source mapping.
