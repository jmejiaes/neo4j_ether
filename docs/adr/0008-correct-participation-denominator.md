# ADR-0008: Correct the total-participation denominator (Query 4.2.3)

- Status: Accepted
- Date: 2026-07-11

## Context

`top_accounts_by_total_pct_query` ("% of total transactions", Query 4.2.3) computed
its denominator as `MATCH (n) WITH COUNT(n)` — i.e. **all nodes** (blocks + users +
external + internal transactions) — while the numerator is an account's
participations (sent + received). The ratio was therefore dimensionally incoherent
(participations ÷ nodes) and mislabeled as "% of transactions".

This denominator was carried over from the original paper's query (`MATCH (tx)`
without a label also matches all nodes). At 100 blocks the distortion is small, but
**at scale it fabricates a false trend.** The number of users per transaction falls
sublinearly as the window grows (a known property of transaction graphs; here
1.00 → 0.22 from 2 to 10,000 blocks), so the all-nodes denominator shrinks relative
to the transaction count and the reported percentage rises **mechanically**, even
when the true concentration is constant.

This was caught while validating the queries against the committed run outputs, and
then verified numerically. WETH at 10,000 blocks: 287,191 participations ÷
2,922,045 nodes = 9.83% (the reported figure). Under a correct denominator the share
is flat:

| window | reported % (all nodes) | % of participations (2·T) |
|-------:|-----------------------:|--------------------------:|
| 2      | 7.00 | 7.00 |
| 10     | 6.51 | 6.03 |
| 50     | 7.19 | 5.76 |
| 100    | 7.87 | 5.92 |
| 1,000  | 9.11 | 5.96 |
| 10,000 | 9.83 | 6.03 |

## Decision

Denominator = **total participations** = count of all `SENT_BY` + `RECEIVED_BY`
relationships (= 2 × #transactions, one sender + one receiver each). The metric is
"share of transaction participations". Query fixed at
`src/ether/db/analytics_queries.py`; chart/table labels updated to "participations".

The corrected within-era finding is **stability, not sharpening**: WETH holds ~6%
of participations at every window size (slightly higher at the smallest window).

## Consequences

- **Prose corrected** in `paper_v2.md`: abstract, §4.3 ("Concentration is stable…"),
  §5.2, §5.4, §6, and the Figure 5 caption. The "concentration sharpens with scale"
  narrative is removed; the honest claim is stability across four orders of magnitude.
- **Artifacts regenerated** from the committed CSVs (no re-run needed): Table A.2,
  Figure 5 (within-era, curves now overlap), Figure 7 (cross-era, now free of the
  uneven all-nodes inflation — the "2023 is flattest at the head" observation
  survives and is now trustworthy).
- **Unaffected:** all rankings (WETH #1, stable top-3), raw sent/received counts,
  cross-era densification and internal/external-ratio findings, and Tables A.1/A.3–A.6.
- Lesson: percentage metrics need an explicitly defined, dimensionally coherent
  denominator; scaling can turn a latent small-sample mislabel into a headline error.
