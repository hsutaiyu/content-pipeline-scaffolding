# OV Content Pipeline — SPEC

An agentic pipeline that turns raw source material into publication-ready drafts.
Three stage-scoped agents — **distiller → ideator → drafter** — run as stateless
transforms, with two human gates (idea selection, draft approval) worked entirely
in Notion.

```mermaid
flowchart LR
    subgraph Sources
        A[Day.ai summaries]
        B[Meeting digests]
        C[Case-study / topic searches]
        D[Content bank + voice guidelines]
    end
    subgraph Ingest["Ingest (scheduled job)"]
        E[Adapters → feed/raw/]
    end
    subgraph Runtime["GitHub Actions"]
        F[Distiller]
        G[Ideator]
        H[Drafter]
    end
    subgraph Notion["Notion — state + human surface"]
        I[(Distilled Notes)]
        J[Storybook state + published log]
        K[(Idea Cards)]
        L[Draft pages]
    end
    A & B & C --> E
    E --> F
    D --> F
    F --> I
    I --> G
    J <--> G
    G --> K
    K -- "status: chosen (gate 1)" --> H
    H --> L
    L -- "review: approved (gate 2)" --> M[Final edit → content calendar]
    M -- "status: published" --> J
```

## Components

### 1. Sources and ingestion

Every source is an independent adapter whose only job is to drop a dated markdown
file into `feed/raw/<source>/`. Adding a source means adding an adapter; the core
never changes. Adapters run on a schedule on the operator's machine and push
commits to this repo. The content bank and voice guidelines live in the repo and
are read directly — no adapter needed.

Raw feed never leaves the repo and never reaches the drafting stage.

### 2. Distiller

Trigger: push to `feed/raw/**`.

Compresses each raw file into a structured note: claims, case studies, quotable
lines, why it matters to the thesis, which storybook beats it touches. Output is
strict JSON between stages, written as a row in the **Distilled Notes** database.

### 3. Narrative state

A `Storybook / State` page tracks where the content arc stands: current chapter,
the question it opened with, the question it must hand off, beats in play,
real-world anchors. A `Storybook / Published Log` records what has shipped. The
ideator reads both — and writes back — so the pipeline has memory and does not
re-propose published angles.

### 4. Ideator

Trigger: daily schedule.

Matches fresh distilled notes to the current chapter's question and creates
**Idea Card** rows (`status: proposed`): hook, chapter and question served, beats
touched, suggested format, and citations back to the distilled notes.

### 5. Gate 1 — idea selection (human)

The team opens the *Ideas awaiting selection* view in Notion, reads cards, and
sets `status` to `chosen` or `rejected`. That dropdown flip is the entire
interface — no terminal, no GitHub.

### 6. Drafter

Trigger: poll schedule + manual dispatch.

Picks up cards with `status: chosen`, combines the card, its linked distilled
notes, the matching format rules, and the voice guidelines, and produces a draft
page in Notion. Sets `status: drafted`, `review: pending`. The drafter never
sees raw feed — its context stays clean.

### 7. Gate 2 — draft approval (human)

The *Drafts awaiting approval* view surfaces drafts with `review: pending`.
Approval moves the piece to final edit and the content calendar; shipping sets
`status: published`, which closes the loop back into the published log.

## Notion surface

| Object | Type | Purpose |
|---|---|---|
| Idea Cards | database | one row per content idea, `proposed → chosen → drafted → published/rejected` |
| Distilled Notes | database | one row per distilled raw input, with source, date, beats |
| Storybook / State, Published Log | pages | narrative arc state and ship history |
| Voice / Guidelines, Formats / * | pages | drafting rules, one page per format |
| Drafts | pages | linked from their idea card |

Two filtered views, shared as URLs, are the team's entire interface:
*Ideas awaiting selection* (`status = proposed`) and
*Drafts awaiting approval* (`status = drafted`, `review = pending`).

## Runtime

| Workflow | Trigger | Does |
|---|---|---|
| `distill.yml` | push to `feed/raw/**`, manual | raw files → Distilled Notes rows |
| `ideate.yml` | daily schedule, manual | notes + storybook state → Idea Card rows |
| `draft.yml` | 15-min poll, manual dispatch | chosen cards → draft pages |

## Configuration

All environment- and provider-specific values are secrets, never code:

| Secret | Purpose |
|---|---|
| `NOTION_API_KEY` | integration token scoped to the pipeline pages |
| `NOTION_ROOT_PAGE_ID` | root page under which all databases live |
| `LLM_BASE_URL` | OpenAI-compatible API endpoint |
| `LLM_API_KEY` | provider key |

Prompts are stable, provider-agnostic, and live in `prompts/`. No stage depends
on a specific model; switching providers is a settings change.

## Design principles

- **Three stage-scoped agents**, not one end-to-end agent: cadences differ, the
  drafter's context must stay clean, and a broken source must not block drafting.
- **Structured handoffs:** stages exchange strict JSON and database rows, so
  behavior is deterministic and auditable.
- **Humans decide, agents prepare:** automation stops at the two gates.
- **Exit ramp:** prompts, adapters, and the raw corpus live in git; Notion state
  exports via the API. Nothing is locked into a vendor.
