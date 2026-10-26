---
source: casebank
date: '2026-10-26'
area: Registries and identity
chapters:
- 8 · Will It Still Hold?
flags: []
article: https://blog.cloudflare.com/pq-2025/
---

# Cloudflare: state of the post-quantum Internet in 2025

**What happened:** Cloudflare reported that more than half of human-initiated traffic it handles uses post-quantum key agreement (Chrome made hybrid ML-KEM default in Chrome 131, November 2024, per search results). Post-quantum signatures, which authenticate who said what, lag well behind because the keys and signatures are much larger; ML-DSA-44 would add about 15 kB per connection.

**Thesis tie:** Post-quantum foundations. Confidentiality is moving fast; authenticity of records (signatures) is the slow, hard part, and that is the part shared records depend on.

**Post angle:** Half the web's human traffic went post-quantum in about a year, yet the signatures that prove who said what barely moved. Records that must stay provable for decades sit on the slower track.

**Caution:** Cloudflare is a vendor; present the numbers as its measurements.

**Source:** "State of the post-quantum Internet in 2025", Bas Westerbaan, Cloudflare Blog, 28 October 2025
