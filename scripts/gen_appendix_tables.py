import pandas as pd, os

R = "data/results"
def short(a): return a if not isinstance(a,str) or not a.startswith("0x") else a[:6]+"…"+a[-4:]
def csv(era,n,q):
    p=f"{R}/{era}/{n}/{q}.csv"; return pd.read_csv(p) if os.path.exists(p) else None
def eth(x): return f"{x:,.2f}"
def intf(x): return f"{int(x):,}"

out=[]
w=out.append

w("## Appendix A — Result tables\n")
w("Curated results referenced in Section 4. Full per-run tables (all queries, all "
  "cut-offs and eras) and comparison pivots are also available under "
  "`data/results/<era>/<n>/` and `data/output/`.\n")
w("The ETH totals in Tables A.1 and A.6 sum external-transaction value and "
  "internal-transaction amount over incoming edges, so ETH forwarded through a "
  "contract may be counted at more than one hop; these tables are intended for "
  "ranking, not exact fund accounting.\n")

# A.1 top received / sent, 2024 @ 10k
rec=csv("recent_2024",10000,"query_1/query_1_1").head(10).reset_index(drop=True)
snt=csv("recent_2024",10000,"query_1/query_1_2").head(10).reset_index(drop=True)
w("### Table A.1 — Top-ten accounts by total ETH received and sent (post-Dencun 2024, 10,000 blocks)\n")
w("| Rank | Account (received) | ETH received | Account (sent) | ETH sent |")
w("|-----:|--------------------|-------------:|----------------|---------:|")
for i in range(10):
    w(f"| {i+1} | {short(rec.account[i])} | {eth(rec.total_received[i])} | {short(snt.account[i])} | {eth(snt.total_sent[i])} |")
w("")

# A.2 participation, 2024 @ 10k
p=csv("recent_2024",10000,"query_2/query_2_3").head(10).reset_index(drop=True)
w("### Table A.2 — Top-ten accounts by transaction-participation percentage (post-Dencun 2024, 10,000 blocks)\n")
w("| Rank | Account | Sent tx | Received tx | Total participation (%) |")
w("|-----:|---------|--------:|------------:|------------------------:|")
for i in range(10):
    w(f"| {i+1} | {short(p.account[i])} | {intf(p.sent_transactions[i])} | {intf(p.received_transactions[i])} | {p.total_percentage[i]:.2f} |")
w("")

# A.3 statistics across ladder, 2024
LAD=[2,10,50,100,1000,10000]
def stat_table(q, amt, title):
    w(f"### {title}\n")
    w("| Blocks | Average | Minimum | Maximum | P25 | Median | P75 |")
    w("|-------:|--------:|--------:|--------:|----:|-------:|----:|")
    for n in LAD:
        d=csv("recent_2024",n,q)
        if d is None: continue
        r=d.iloc[0]
        cols=[f"average_{amt}",f"minimum_{amt}",f"maximum_{amt}",
              "percentile_25",f"median_{amt}","percentile_75"]
        vals=" | ".join(f"{r[c]:,.4f}" for c in cols)
        w(f"| {n:,} | {vals} |")
    w("")
stat_table("query_4/query_4_1","value","Table A.3 — External-transaction value statistics across the block-count ladder (post-Dencun 2024, ETH)")
stat_table("query_4/query_4_2","amount","Table A.4 — Internal-transaction amount statistics across the block-count ladder (post-Dencun 2024, ETH)")

# A.5 top pairs 2024 @10k
pc=csv("recent_2024",10000,"query_5/query_5_1").head(10).reset_index(drop=True)
pv=csv("recent_2024",10000,"query_6/query_6").head(10).reset_index(drop=True)
w("### Table A.5 — Top-ten sender→receiver pairs (post-Dencun 2024, 10,000 blocks)\n")
w("| Rank | Pair (by tx count) | Tx count | Pair (by ETH) | ETH transferred |")
w("|-----:|--------------------|---------:|---------------|----------------:|")
for i in range(10):
    pair_c=f"{short(pc.sender[i])}→{short(pc.receiver[i])}"
    pair_v=f"{short(pv.sender[i])}→{short(pv.receiver[i])}"
    w(f"| {i+1} | {pair_c} | {intf(pc.transaction_count[i])} | {pair_v} | {eth(pv.total_value_sent[i])} |")
w("")

# A.6 cross-era top-5 received @10k
eras=[("early_2016","2016"),("defi_summer_2020","2020"),("post_merge_2023","2023"),("recent_2024","2024")]
tops={lab:csv(e,10000,"query_1/query_1_1").head(5).reset_index(drop=True) for e,lab in eras}
w("### Table A.6 — Top-five accounts by total ETH received, per era (10,000-block windows)\n")
w("| Rank | 2016 | 2020 | 2023 | 2024 |")
w("|-----:|------|------|------|------|")
for i in range(5):
    cells=[]
    for _,lab in eras:
        d=tops[lab]; cells.append(f"{short(d.account[i])} ({eth(d.total_received[i])})")
    w(f"| {i+1} | "+" | ".join(cells)+" |")
w("")

open("docs/paper/appendix_tables.md","w").write("\n".join(out)+"\n")
print("wrote docs/paper/appendix_tables.md")
print("=== preview (first 40 lines) ===")
print("\n".join(out[:40]))
