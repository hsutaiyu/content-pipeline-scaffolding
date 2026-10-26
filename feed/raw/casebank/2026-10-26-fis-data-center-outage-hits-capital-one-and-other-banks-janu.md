---
source: casebank
date: '2026-10-26'
area: Reconciliation in finance
chapters:
- 1 · The Trust Bridge
flags: []
article: https://www.nbcnews.com/business/business-news/capital-one-acknowledges-outage-users-report-issues-accessing-deposits-rcna187966
---

# FIS data-center outage hits Capital One and other banks, January 2025

**What happened:** A local power outage at a data center run by FIS, a core-processing vendor, left Capital One customers unable to see deposits or make payments for several days starting 15 to 16 January 2025. Capital One said functionality was restored on 19 January. Other reports (search-confirmed, not this page) say 26 other banks were affected. FIS said it was working with clients to post the transactions that had happened while systems were offline.

**Thesis tie:** Events vs state. The events (payments, deposits) kept happening while the system that derives balances was down; recovery meant replaying them into state afterwards.

**Post angle:** Actor: a bank and its core vendor. Decision: queue the transactions and post them after recovery. Consequence: customers saw balances that lagged reality for days.

**Caution:** Consumer-harm story; keep it about the mechanism. Don't blame FIS or Capital One. The "26 other banks" figure isn't on the NBC page.

**Source:** NBC News, "Capital One outage drags into Friday afternoon, leaving some customers without deposit access," 17 January 2025
