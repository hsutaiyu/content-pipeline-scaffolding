---
source: casebank
date: '2026-10-26'
area: Registries and identity
chapters:
- 3 · What Would Have to Be True
- 7 · Who Goes First?
flags:
- Strong pick
article: https://www.rfc-editor.org/rfc/rfc9162.html
---

# Certificate Transparency: RFC 9162 (CT version 2.0)

**What happened:** The IETF specification defines CT as a set of append-only, publicly auditable logs of issued TLS certificates. The logs record that a certificate was issued; they do not decide whether it should have been. Detection and judgement are left to monitors, browsers and the certificate authorities themselves.

**Thesis tie:** The cleanest working precedent for event-state dissociation. A minimal service records events and their order and keeps them available; every party (browser, CA, domain owner) derives its own conclusions under its own rules.

**Post angle:** The web's certificate authorities agreed more than a decade ago to publish every certificate to logs that never judge them. Browsers decide trust; logs only keep the record. That split is why it works across competing companies.

**Caution:** CT is from 2013 (RFC 6962) and revised in 2021, so it is not "news". Frame it as proof the pattern already runs at Internet scale, not as a template Open Value copies.

**Source:** RFC 9162, "Certificate Transparency Version 2.0", IETF (B. Laurie and E. Messeri of Google, R. Stradling of Sectigo), December 2021
