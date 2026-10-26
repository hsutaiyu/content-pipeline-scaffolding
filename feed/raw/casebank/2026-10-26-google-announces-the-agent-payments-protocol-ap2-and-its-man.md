---
source: casebank
date: '2026-10-26'
area: AI agents
chapters:
- 2 · For Us Not By Us
- 9 · Who Said You Could?
flags: []
article: https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol
---

# Google announces the Agent Payments Protocol (AP2) and its "mandates"

**What happened:** Google published AP2 as an open protocol for agent-initiated payments, built with more than 60 organisations including Adyen, American Express, Coinbase, Etsy, Mastercard, PayPal, Revolut, Salesforce, UnionPay International and Worldpay. It uses signed "mandates" (an Intent Mandate, then a Cart Mandate the user approves) as verifiable proof of what the user instructed. Google lists "determining accountability if a fraudulent or incorrect transaction occurs" as one of the problems the protocol is meant to address.

**Thesis tie:** Events vs state. The mandate is a signed record of an event (the user said yes to this cart at this price); what that event means for liability is still decided by each network's rules. Also AI agents crossing organisations: user, agent platform, merchant, network and issuer are five separate systems.

**Post angle:** A shopper approves a cart through an agent; Google's answer is a signed record of the approval. The open question for the industry is where that record lives and who can read it when the merchant, the issuer and the agent platform disagree.

**Caution:** Google-authored; describe AP2 as Google's design, not an adopted industry standard. Do not suggest mandates are insufficient.

**Source:** "Announcing Agent Payments Protocol (AP2)", Google Cloud blog, Stavan Parikh (VP/GM Payments, Google) and Rao Surapaneni (VP/GM, Google Cloud), 16 September 2025
