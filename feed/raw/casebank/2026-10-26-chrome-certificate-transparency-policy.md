---
source: casebank
date: '2026-10-26'
area: Registries and identity
chapters:
- 7 · Who Goes First?
- 10 · The Mosaic
flags: []
article: https://googlechrome.github.io/CertificateTransparency/ct_policy.html
---

# Chrome Certificate Transparency Policy

**What happened:** Chrome only trusts a publicly issued certificate if it carries signed timestamps (SCTs) from CT logs: two or three depending on certificate lifetime. The policy requires that the logs be run by distinct operators, so no single log operator's word is enough. Search results (Chromium ct-policy group) confirm that from 15 April 2022 Chrome dropped the earlier requirement for one Google-operated log.

**Thesis tie:** Neutral ordering without a single owner. The record is trusted because independent operators hold it, and the relying party (the browser) applies its own policy.

**Post angle:** Google removed the rule that one of the logs had to be its own. The decision made the record more credible by making Google less central.

**Caution:** Avoid implying browsers "police" CAs in an adversarial way; CAs helped build CT.

**Source:** "Chrome Certificate Transparency Policy", Google Chrome (googlechrome.github.io), current policy page
