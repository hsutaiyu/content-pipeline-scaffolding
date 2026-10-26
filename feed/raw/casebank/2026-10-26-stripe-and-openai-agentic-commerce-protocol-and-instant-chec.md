---
source: casebank
date: '2026-10-26'
area: AI agents
chapters:
- 2 · For Us Not By Us
flags:
- Check before use
article: https://stripe.com/newsroom/news/stripe-openai-instant-checkout
---

# Stripe and OpenAI: Agentic Commerce Protocol and Instant Checkout

**What happened:** OpenAI launched in-chat purchasing in ChatGPT for US Etsy sellers, with "over a million" Shopify merchants announced as coming. Stripe introduced the Shared Payment Token, which lets an app like ChatGPT initiate payment without exposing the buyer's credentials, and released the Agentic Commerce Protocol as an open standard (agenticcommerce.dev) usable without Stripe as processor.

**Thesis tie:** Events vs state. The agent platform carries the event (this buyer wants this item); the merchant keeps its own state (order, tax, returns). Two independent systems, one transaction.

**Post angle:** Pair with item 6. The design kept the merchant as the system of record for the order, and the chat as the place the decision happened.

**Caution:** OpenAI's own announcement (openai.com/index/buy-it-in-chatgpt) returned 403; use Stripe's release.

**Source:** "Stripe powers Instant Checkout in ChatGPT and releases Agentic Commerce Protocol codeveloped with OpenAI", Stripe newsroom, 29 September 2025
