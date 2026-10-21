# OV Content Pipeline

Agentic content pipeline: raw source material → distilled notes → idea cards →
drafts, with human gates for idea selection and draft approval.

- **State + human surface:** Notion (two databases, filtered views for the gates)
- **Code, prompts, raw corpus:** this repo
- **Runtime:** GitHub Actions

The pipeline is a state machine: transitions fire only on a cron tick or a
button press. AI appears in exactly three places — distiller, ideator, drafter.
See SPEC.md for the design.

## Setup

1. Create a Notion integration; share the pipeline root page and the two source
   databases with it.
2. Repo secrets: `NOTION_API_KEY`, `NOTION_ROOT_PAGE_ID`, `LLM_BASE_URL`,
   `LLM_API_KEY`, `LLM_MODEL`.
3. Run the **init** workflow (Actions → init → Run workflow). It provisions the
   Notion databases and pages, ingests the sources, and distills them.
4. In Notion, add two filtered views on Idea Cards: `status = proposed`
   ("Ideas awaiting selection") and `status = drafted AND review = pending`
   ("Drafts awaiting approval"). Bookmark both — they are the team's interface.

## Buttons (Actions → workflow → Run workflow)

| Button | Does |
|---|---|
| **init** | Provision Notion → ingest → distill. Zero to ready. |
| **ideate** | Generate idea cards (`proposed`) from fresh distilled notes. |
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

Stages run locally with the same entry points as CI
(`uv run python -m src.distill` etc.); `notion_ids.json` must exist
(created by init).
