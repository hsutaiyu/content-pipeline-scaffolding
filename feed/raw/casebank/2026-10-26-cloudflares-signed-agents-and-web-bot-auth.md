---
source: casebank
date: '2026-10-26'
area: AI agents
chapters:
- 5 · Who's Really There?
flags: []
article: https://blog.cloudflare.com/signed-agents/
---

# Cloudflare's "signed agents" and Web Bot Auth

**What happened:** Cloudflare created a "signed agents" classification for agents "directed by an end user instead of a single company", verified via Web Bot Auth (HTTP message signatures). Launch partners were OpenAI's ChatGPT agent, Block's Goose, Browserbase and Anchor Browser.

**Thesis tie:** AI agents crossing organisations. Identity of the agent is proven per request; it says who is asking, not what was agreed. Useful to show that identity and history are separate problems.

**Post angle:** Websites now verify agents by signature at the door. What the agent does once inside, and what each side records about it, is a separate question.

**Caution:** Technical; keep the post on the idea, not the cryptography.

**Source:** "The age of agents: cryptographically recognizing agent traffic", Cloudflare blog, 28 August 2025
