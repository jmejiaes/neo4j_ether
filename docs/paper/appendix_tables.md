## Appendix A — Result tables

Curated results referenced in Section 4. Full per-run tables (all queries, all cut-offs and eras) and comparison pivots are also available under `data/results/<era>/<n>/` and `data/output/`.

The ETH totals in Tables A.1 and A.6 sum external-transaction value and internal-transaction amount over incoming edges, so ETH forwarded through a contract may be counted at more than one hop; these tables are intended for ranking, not exact fund accounting.

### Table A.1 — Top-ten accounts by total ETH received and sent (post-Dencun 2024, 10,000 blocks)

| Rank | Account (received) | ETH received | Account (sent) | ETH sent |
|-----:|--------------------|-------------:|----------------|---------:|
| 1 | 0xc02a…6cc2 | 198,186.49 | 0xc02a…6cc2 | 150,524.44 |
| 2 | 0x0000…05fa | 124,741.00 | 0x28c6…1d60 | 121,171.97 |
| 3 | 0xb5d8…f511 | 97,121.07 | 0xb5d8…f511 | 103,128.36 |
| 4 | 0x28c6…1d60 | 87,524.79 | 0xae7a…fe84 | 95,596.98 |
| 5 | 0xa9d1…3e43 | 69,661.62 | 0x889e…f9b1 | 73,291.14 |
| 6 | 0x1714…17eb | 50,906.99 | 0xa9d1…3e43 | 67,164.87 |
| 7 | 0xae7a…fe84 | 50,906.99 | 0xceb6…66ea | 61,343.35 |
| 8 | 0x8934…b2b9 | 49,121.18 | 0x8934…b2b9 | 49,121.18 |
| 9 | 0xc364…fe88 | 41,233.48 | 0xf2f3…0d60 | 45,234.17 |
| 10 | 0xceb6…66ea | 41,177.70 | 0xfddf…2999 | 44,672.00 |

### Table A.2 — Top-ten accounts by transaction-participation percentage (post-Dencun 2024, 10,000 blocks)

| Rank | Account | Sent tx | Received tx | Total participation (%) |
|-----:|---------|--------:|------------:|------------------------:|
| 1 | 0xc02a…6cc2 | 127,869 | 159,322 | 6.03 |
| 2 | 0x3fc9…7fad | 63,351 | 106,654 | 3.57 |
| 3 | 0xdac1…1ec7 | 0 | 158,362 | 3.33 |
| 4 | 0x7a25…488d | 57,572 | 74,887 | 2.78 |
| 5 | 0x3328…9c49 | 62,174 | 39,332 | 2.13 |
| 6 | 0x80a6…5d9e | 53,603 | 38,130 | 1.93 |
| 7 | 0xa0b8…eb48 | 0 | 48,392 | 1.02 |
| 8 | 0x1111…0582 | 14,653 | 23,269 | 0.80 |
| 9 | 0x3a10…981f | 22,835 | 13,160 | 0.76 |
| 10 | 0xa69b…e78c | 20,955 | 12,285 | 0.70 |

### Table A.3 — External-transaction value statistics across the block-count ladder (post-Dencun 2024, ETH)

| Blocks | Average | Minimum | Maximum | P25 | Median | P75 |
|-------:|--------:|--------:|--------:|----:|-------:|----:|
| 2 | 0.1225 | 0.0000 | 7.4514 | 0.0000 | 0.0000 | 0.0223 |
| 10 | 0.4178 | 0.0000 | 199.0352 | 0.0000 | 0.0000 | 0.0300 |
| 50 | 0.8540 | 0.0000 | 1,462.0000 | 0.0000 | 0.0000 | 0.0200 |
| 100 | 1.1449 | 0.0000 | 2,505.7346 | 0.0000 | 0.0000 | 0.0206 |
| 1,000 | 1.9498 | 0.0000 | 17,536.8474 | 0.0000 | 0.0000 | 0.0450 |
| 10,000 | 1.1807 | 0.0000 | 17,568.3202 | 0.0000 | 0.0000 | 0.0292 |

### Table A.4 — Internal-transaction amount statistics across the block-count ladder (post-Dencun 2024, ETH)

| Blocks | Average | Minimum | Maximum | P25 | Median | P75 |
|-------:|--------:|--------:|--------:|----:|-------:|----:|
| 2 | 0.5514 | 0.0000 | 50.0000 | 0.0109 | 0.0466 | 0.1178 |
| 10 | 6.0682 | 0.0000 | 512.0000 | 0.0063 | 0.0424 | 0.1507 |
| 50 | 3.4190 | 0.0000 | 1,462.0000 | 0.0063 | 0.0419 | 0.1500 |
| 100 | 2.7065 | 0.0000 | 1,462.0000 | 0.0050 | 0.0380 | 0.1384 |
| 1,000 | 2.3793 | 0.0000 | 4,500.0000 | 0.0115 | 0.0626 | 0.2040 |
| 10,000 | 1.9225 | 0.0000 | 28,382.1031 | 0.0050 | 0.0429 | 0.1874 |

### Table A.5 — Top-ten sender→receiver pairs (post-Dencun 2024, 10,000 blocks)

| Rank | Pair (by tx count) | Tx count | Pair (by ETH) | ETH transferred |
|-----:|--------------------|---------:|---------------|----------------:|
| 1 | 0xae2f…ae13→0x1f2f…f387 | 8,097 | 0xb5d8…f511→0xa9d1…3e43 | 60,722.48 |
| 2 | 0x0000…cbe0→0x68d3…0dc9 | 5,303 | 0x28c6…1d60→0xdfd5…963d | 32,049.43 |
| 3 | 0x0000…4a5f→0x68d3…0dc9 | 5,301 | 0xcfec…9ff5→0x0000…05fa | 24,544.00 |
| 4 | 0x4634…9758→0xdac1…1ec7 | 3,770 | 0x28c6…1d60→0x21a3…5549 | 21,588.05 |
| 5 | 0x7830…6f43→0xa9d1…3e43 | 3,272 | 0x28c6…1d60→0x4976…2327 | 20,369.97 |
| 6 | 0x9379…7551→0x68d3…6fbf | 2,896 | 0x28c6…1d60→0x56ed…b17f | 19,567.25 |
| 7 | 0x89e5…7c40→0xdac1…1ec7 | 2,716 | 0xfae1…4cf6→0xcd53…ca7b | 17,568.32 |
| 8 | 0x355d…09d5→0xaf12…d58e | 2,635 | 0xbe9f…696b→0xceb6…66ea | 17,536.85 |
| 9 | 0x4481…5af8→0x68d3…6fbf | 2,610 | 0xfaff…4497→0xceb6…66ea | 17,513.06 |
| 10 | 0x56ed…b17f→0xdac1…1ec7 | 2,283 | 0xceb6…66ea→0x930f…c785 | 17,491.36 |

### Table A.6 — Top-five accounts by total ETH received, per era (10,000-block windows)

| Rank | 2016 | 2020 | 2023 | 2024 |
|-----:|------|------|------|------|
| 1 | 0xaa1a…6444 (2,938,082.38) | 0x7a25…488d (536,109.63) | 0x8358…28fe (181,792.00) | 0xc02a…6cc2 (198,186.49) |
| 2 | 0x32be…2d88 (2,322,598.73) | 0xc02a…6cc2 (519,004.51) | 0xc02a…6cc2 (144,639.95) | 0x0000…05fa (124,741.00) |
| 3 | 0xbfc3…5bdd (2,276,719.06) | 0x3f5c…f0be (231,722.33) | 0xef1c…bf6b (43,212.43) | 0xb5d8…f511 (97,121.07) |
| 4 | 0x04c9…3ee5 (775,333.68) | 0x8358…28fe (141,912.00) | 0x28c6…1d60 (42,099.06) | 0x28c6…1d60 (87,524.79) |
| 5 | 0xd5c6…06b7 (775,333.00) | 0xfa52…40b3 (85,549.30) | 0xc364…fe88 (36,557.31) | 0xa9d1…3e43 (69,661.62) |

