# Bucket 2 Semantic layer

<!-- Snapshot of the “Low level content” sheet (research-call lines, as of Oct 12, 2026). Ported 2026-10-21. -->

These are the scenes and use cases from the calls, grouped by where the base layer would be used. The LoPucki debrief applies to all of them: lead with the business process, then the agent.

| Theme | Line | Source | Edit |
|---|---|---|---|
| Agents need what employees have | “An agent is basically an employee.” | Andreas · Leonard Rosenthol, Adobe · Sep 17 · notes | As said. |
| Agents need what employees have | “Before two companies’ agents can deal with each other, each needs three things the other can check: a legal identity, a power of attorney that sets its scope, and a history of how it has behaved.” | Andreas · Carmit Hazay and Muthu Venkitasubramaniam, Ligero · Sep 3; Ángel Sánchez · Oct 8 · notes | Built from his three prerequisites. |
| Agents need what employees have | “An agent might be allowed to request quotes but not place orders. Today nothing machine-checkable says so.” | Andreas · Atul Prakash, Michigan · Sep 21 · notes | Built from his scope example. |
| Agents need what employees have | “If you don’t have that, you cannot establish a point of irrevocable liability.” | Andreas · Mahesh Balakrishnan, Meta · Sep 15 | As said. Name “that” in the line before: legal identity plus power of attorney. |
| Agents need what employees have | “Without legal identity, delegation is impossible, and insurance won’t pay when an agent misbehaves.” | Andreas · Philipp Jovanovic, UCL · Oct 2 · notes | Built from. |
| Agents need what employees have | “Agent activity today is 100% uninsurable.” | Andreas · Shabsi Walfish, Google · Sep 17 · notes | As said. A consequence line: follow it with the fix, not the alarm. |
| Agents need what employees have | “The agent has no access, and you give it a credential before it can even act.” | Andreas · Ning Luo, UIUC · Sep 30 · notes | Trimmed. Zero trust as an inverted default. |
| Agents need what employees have | “Assume the counterparty’s agent is compromised until it proves otherwise.” | Andreas · Vishal Sachdev, UIUC · Sep 16 · notes | Built from his zero-trust point. |
| Agents need what employees have | “An API gateway could check an agent’s identity and scope and turn it away before it does anything, even if the agent only lives for five minutes.” | Andreas · Nikhil Swamy, Microsoft Research · Oct 7 · notes | Built from. |
| Agents need what employees have | “Without a provable execution trail, it’s a hard stop.” | Andreas · Vishal Sachdev · Sep 16 · notes | As said. |
| Telcos and networks on demand | “Buy a secure data connection between Singapore and New York, on demand, for an hour.” | Andreas · Ning Luo · Sep 30 · notes | Built from. The scene that opens his telco story. |
| Telcos and networks on demand | “A network-as-a-service deal that lasts five minutes has to be requisitioned and settled in seconds.” | Andreas · Yale applied cryptography group · Sep 25 · notes | Built from. |
| Telcos and networks on demand | “A single carrier can see tens of thousands of agent-to-agent commercial transactions a day, each needing automated mediation.” | Andreas · Pratyush Mishra, UPenn · Sep 25 · notes | Built from. The figure is his per-carrier estimate; check it before publishing. |
| Finance and enterprise | “The order itself is the contract, the way it is when you buy something on Amazon.” | Andreas · Philipp Jovanovic · Oct 2 · notes | Built from. An anchor for automated contract negotiation. |
| Finance and enterprise | “Requests for quotes, orders, fulfillment, invoicing, settlement: every step needs semantics both sides agree on.” | Andreas · Sanjam Garg, Berkeley · Aug 3 · notes | Built from. |
| Finance and enterprise | “Use cases on the table include atomic asset exchange and escrow whose terms and conditions are encoded as proofs.” | Andreas · Nitin Singh, IBM Research · Sep 15 · notes | Built from. |
| Finance and enterprise | “Building trust company by company is slow and contract-heavy, and it’s part of why ERP implementations fail.” | Andreas · Atul Prakash · Sep 21 · notes | Built from. |
| Finance and enterprise | “I’ve done more ERP implementations and outsourcing programs than I actually remember.” | Andreas · Alysson Bessani, University of Lisbon · Aug 25 | Andreas’s handle only. Credibility before an ERP point. |
| Finance and enterprise | “An exchange can be asked by a regulator to show user activity across 25 chains, with nothing built to do it.” | Jack and Andreas · Andreas Park, Toronto Rotman · Aug 19 · notes | Built from their example. Park thought even this single-party use was worth having. Don’t name the exchange without checking. |
| Trust graphs | “A cryptographically verifiable Google or Yelp review of a business.” | Andreas · Ángel Sánchez, Madrid · Oct 8 · notes | As said. A variant of his Yelp anchor. |
| Trust graphs | “A trust graph is a sequence of reviews in which each counterparty confirms a transaction went as agreed.” | Andreas · Philipp Jovanovic · Oct 2 · notes | Built from. |
| Trust graphs | “Faking a long history takes real time.” | Andreas · Ning Luo · Sep 30 · notes | Built from “faking a long history requires real time investment.” |
| Trust graphs | “Anonymous entries would naturally count for less than identity-attested ones.” | Andreas · Josh Benaloh, Microsoft Research · Sep 16 · notes | Built from. |
| Trust graphs | “Think of it as automated KYC with an audit trail.” | Andreas · Ghassan Karame, Bochum · Sep 28 · notes | Built from. |
| Trust graphs | “Each company publishes a verifiable history of its economic activity and a dictionary of what its terms mean, so a counterparty can reason about its track record.” | Andreas · Atul Prakash · Sep 21 · notes | Built from. |
| Trust graphs | “A proof of correct execution can show a business process ran as promised without exposing the inputs.” | Andreas · Atul Prakash · Sep 21 · notes | Built from his answer on privacy. |
| Trust graphs | “From peer, to trust bridge, to peer. Then from peer, to shared log, to peer.” | Andreas · Atul Prakash · Sep 21 · notes | Built from. Works as a diagram caption. |
| Security and provenance | “Email that can’t be spoofed, even if the email provider is fully compromised.” | Andreas · Fernando Pedone · Sep 25; Josh Benaloh · Sep 16; Nitin Singh · Sep 15 · notes | Built from. Also the storybook’s planned first chapter (Oct 12 sales sync). |
| Security and provenance | “Prove that an action came from an agent created by a specific organization, with an audit trail anyone can check.” | Andreas · Leonard Rosenthol · Sep 17 · notes | Built from. The content-provenance angle. |
