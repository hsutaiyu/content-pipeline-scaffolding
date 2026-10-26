---
source: casebank
date: '2026-10-26'
area: Reconciliation in finance
chapters:
- 7 · Who Goes First?
- 8 · Will It Still Hold?
flags:
- Strong pick
article: https://www.ecb.europa.eu/press/intro/publications/pdf/ecb.miptopical251107.en.pdf
---

# ECB post-mortem: TARGET Services incident of 27 February 2025

**What happened:** A hardware fault (two redundant Ethernet ports on a storage control unit failing at the same moment) made T2 unavailable for about 10 hours and T2S for about 8. The 60-minute recovery target could not be met because "consistency and integrity checks had to be performed" before restarting on the secondary site. 11,898 messages were rejected because of the "inconsistent state of the system". Payment cut-offs were pushed to 23:00 and midnight and the business date change happened at 01:12. During the outage 146 payments were settled in the ECONS II contingency system; afterwards the balances of 55 contingency accounts had to be transferred back to the main system, and some national central banks' accounting departments asked for those closing balances to be made available in the T2 data warehouse.

**Thesis tie:** Events vs state; reconciliation after disruption. Before restarting, the operator had to confirm that the recorded state could be trusted. Payments made in a separate contingency ledger then had to be folded back into the main one.

**Post angle:** Actor: the Eurosystem's operators. Decision: verify data integrity rather than fail over fast. Consequence: a longer outage, accepted as the price of a trustworthy record. The ECB chose correctness over speed, and the post shouldn't second-guess that.

**Caution:** Do not frame as a failure of the ECB. The vendor called the fault unprecedented. Present it as a careful recovery.

**Source:** European Central Bank, "TARGET Services incident of 27th February 2025: Post-mortem Report," November 2025
