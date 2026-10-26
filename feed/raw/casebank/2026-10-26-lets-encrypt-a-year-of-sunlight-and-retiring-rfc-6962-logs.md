---
source: casebank
date: '2026-10-26'
area: Registries and identity
chapters:
- 3 · What Would Have to Be True
- 8 · Will It Still Hold?
flags: []
article: https://letsencrypt.org/2025/06/11/reflections-on-a-year-of-sunlight
---

# Let's Encrypt: a year of Sunlight, and retiring RFC 6962 logs

**What happened:** Let's Encrypt ran three logs on the new tile-based Static CT API, which publishes the log as static files that any CDN can serve. It reported that a single-server Sunlight log (run by Filippo Valsorda) costs roughly $10,000 a year. It then set its older RFC 6962 logs to go read-only on 30 November 2025 and shut down on 28 February 2026, citing the cost of storing log data in a relational database at Web scale.

**Thesis tie:** A minimal recording layer gets cheaper and simpler precisely because it does no interpretation. Availability is part of the job, which is why the read path became static files.

**Post angle:** The nonprofit that issues most of the web's certificates rebuilt its logs so they could be served like static web pages. Recording without interpreting turned out to be the thing that scales.

**Caution:** Keep it about design, not about the old logs "failing". Avoid technical jargon overload in social copy.

**Source:** "Reflections on a Year of Sunlight", Let's Encrypt, 11 June 2025. "End of Life Plan for RFC 6962 Certificate Transparency Logs", Let's Encrypt, 14 August 2025
