#!/usr/bin/env python3
"""
Issue #29 — Phase 3 normalize (P3-normalize).

UPDATES data/processed/enriched_systems.csv in place, filling exactly ONE column:
    op_margin_q1_normalized_pct  [DERIVE]  = operating margin net of CONFIRMED one-time items.

Owns ONLY: data/processed/enriched_systems.csv, column `op_margin_q1_normalized_pct`
(per contracts.md s4 row "P3 normalize"). Every other column is snapshotted before and
asserted byte-unchanged after. Reads (read-only): the enriched CSV (which already carries
the SEC-confirmed `one_time_items_musd` for the 4 for-profits, written by P2-merge) and the
4 SEC JSONs for provenance cross-checking.

NORMALIZATION RULE
------------------
op_margin_q1_normalized_pct = stated op_margin_pct adjusted ONLY for a CONFIRMED one-timer.

  - The seed `op_margin_pct` (and `op_income_musd`) are AUTHORITATIVE; `op_revenue_musd` is
    Becker's-ROUNDED (notes.md). So we DO NOT recompute margin as 100*inc/rev — that would
    reintroduce ±0.2–0.8pp rounding/reconciliation noise on 14 rows (e.g. Banner's known
    +0.79pp non-reconciliation, Phase-0 flag F2) and manufacture rank moves that are NOT
    one-timers. Movement must come ONLY from sourced one-time adjustments.

  - For the 4 for-profits with an SEC-confirmed normalized margin, we take the SEC pull's
    own normalized figure (source of truth), NOT a recomputation from rounded seed:
      * #1 Tenet -> 16.4%  (sec_THC.json operating_income_normalization_musd
            .normalized_margin_pct_vs_net_op_rev_5368 = 16.4; = $883M / $5,368M, where the
            $413M Conifer "revenue from contract termination" is a SEPARATE line ABOVE
            operating income and NOT inside the $5,368M net op rev). Matches spec ~16-17%.
      * #6 CYH  -> 6.4%   (sec_CYH.json one_time_items.implication_for_normalization:
            "$281M -> ~$191M ... 9.5% -> ~6.4% on $2,965M"; +$90M is a CREDIT embedded
            within operating expenses, inflating operating income, not revenue).
      * #2 HCA  -> 12.0%  (sec_HCA.json for_contracts_one_time_items_musd
            .operating_margin_normalization_impact = "none": reported margin unchanged).
      * #3 UHS  -> 11.2%  (sec_UHS.json same: normalization impact "none").

  - For the other 36 systems: normalized = stated op_margin_pct, UNCHANGED (see ZERO FABRICATION).

CONFIRMED ONE-TIMERS (all from SEC primary filings; see data/raw/SOURCES.md):
  #1  Tenet  one_time=413  (Conifer/CommonSpirit Omnibus early-termination revenue; 10-Q + 8-K, verbatim)
  #2  HCA    one_time=0    (no material OPERATING one-timer; $1M facility-sale rounds to 0; $103M is a TAX benefit below op income)
  #3  UHS    one_time=0    (no material OPERATING one-timer; $5.0M gain-on-sale = 0.1% of revenue)
  #6  CYH    one_time=90   (net +$90M impairment-and-gain-on-sale embedded in operating income; 10-Q)

ZERO FABRICATION (contracts.md s0)
----------------------------------
  - The 36 non-for-profit systems have NO SEC filing and were NOT independently scanned for
    Q1 one-time items (CMS/AHRQ do not surface quarterly one-timers; Becker's CDN = HTTP 403).
    For these, NO one-timer was identified, so the one-timer adjustment is ZERO and
    op_margin_q1_normalized_pct = op_margin_pct (the seed margin, authoritative). This is the
    definitional value of the column ("net of IDENTIFIED one-timers"), NOT a fabricated number.
    It is reported as an ASSUMPTION-LIMITED value (not "confirmed clean") in the run notes.
  - derived_3mo periods (Baylor Scott & White #8, Trinity #29) are NOT a dollar one-timer; their
    margins are real but computed from a derived 3-mo window (9-mo@3/31 minus 6-mo@12/31). The
    derived flag already lives in the SEED `reporting_period` column (unchanged here). Their
    normalized margin = reported margin (no confirmed dollar one-timer), and they are surfaced
    in the report so downstream (charts/cuts) can annotate the period artifact.
"""
import csv
import json
import os

BASE = "/Users/mgc50/Dropbox/1. Worked On FILES/(28) Vitals&Vars/issues/29_hospital_margin_ranking"
ENRICHED = f"{BASE}/data/processed/enriched_systems.csv"

OWNED_COL = "op_margin_q1_normalized_pct"

# ---------------------------------------------------------------- (A) load current enriched CSV
with open(ENRICHED, newline='', encoding='utf-8') as f:
    rdr = csv.DictReader(f)
    COLUMNS = list(rdr.fieldnames)
    rows = list(rdr)
assert len(rows) == 40, f"expected 40 rows in enriched, got {len(rows)}"
assert OWNED_COL in COLUMNS, f"{OWNED_COL} not in enriched columns"
by_key = {(int(r['rank']), r['system_name']): r for r in rows}
keys_before = set(by_key)

# snapshot EVERY column except the one P3 owns, to prove nothing else was touched
NON_OWNED_COLS = [c for c in COLUMNS if c != OWNED_COL]
snapshot_before = {k: {c: by_key[k][c] for c in NON_OWNED_COLS} for k in by_key}

# ---------------------------------------------------------------- (B) read SEC one-timers + normalized margins
# Read-only provenance: (1) the one_time_items_musd we expect on the enriched row, and
# (2) the SEC pull's OWN normalized operating margin (the source-of-truth figure we adopt,
# rather than recomputing from Becker's-rounded seed revenue/income).
def sec_one_time(path):
    with open(path, encoding='utf-8') as fh:
        j = json.load(fh)
    oti = j.get('one_time_items', {})
    fc = oti.get('for_contracts_one_time_items_musd')
    if isinstance(fc, dict) and fc.get('value') is not None:
        return float(fc['value'])
    if oti.get('one_time_items_musd') is not None:
        return float(oti['one_time_items_musd'])
    if oti.get('impairment_and_gain_on_sale_of_businesses_net_musd') is not None:
        return float(oti['impairment_and_gain_on_sale_of_businesses_net_musd'])
    return None

sec_files = {1: "sec_THC.json", 2: "sec_HCA.json", 3: "sec_UHS.json", 6: "sec_CYH.json"}
sec_confirmed = {rk: sec_one_time(f"{BASE}/data/raw/{fn}") for rk, fn in sec_files.items()}

# SEC pulls' own normalized operating margin (sourced figure, traced to the JSON field cited).
# THC: operating_income_normalization_musd.normalized_margin_pct_vs_net_op_rev_5368 = 16.4
# CYH: implication_for_normalization narrative "9.5% -> ~6.4%"  -> 6.4
# HCA/UHS: normalization impact "none" -> normalized == reported (12.0 / 11.2)
import re as _re
_cyh = json.load(open(f"{BASE}/data/raw/sec_CYH.json", encoding='utf-8'))
# parse the second percentage in CYH's normalization narrative ("...from ~9.5% to ~6.4%...")
_cyh_norm = float(_re.findall(r'([0-9]+\.[0-9]+)%',
                  _cyh['one_time_items']['implication_for_normalization'])[1])
SEC_NORMALIZED_PCT = {
    1: json.load(open(f"{BASE}/data/raw/sec_THC.json", encoding='utf-8'))
        ['operating_income_normalization_musd']['normalized_margin_pct_vs_net_op_rev_5368'],  # 16.4
    6: _cyh_norm,  # sec_CYH.json one_time_items.implication_for_normalization -> 6.4
    2: None,  # HCA: normalization impact "none" -> use seed stated margin (12.0)
    3: None,  # UHS: normalization impact "none" -> use seed stated margin (11.2)
}

# ---------------------------------------------------------------- (C) compute normalized margin
def to_float(s):
    s = (s or '').strip()
    return float(s) if s != '' else None

detail = []   # per-row audit trail
for k in sorted(by_key):
    rank, name = k
    r = by_key[k]
    mar = to_float(r['op_margin_pct'])           # AUTHORITATIVE stated margin
    ot_raw = (r['one_time_items_musd'] or '').strip()
    ot = to_float(ot_raw)                          # None if empty
    period = r['reporting_period']
    assert mar is not None, f"rank {rank} {name}: stated op_margin_pct missing"

    if rank in sec_confirmed:
        # one of the 4 SEC for-profits: provenance guard + adopt SEC's normalized figure
        sec_val = sec_confirmed[rank]
        assert sec_val is not None, f"SEC json for rank {rank} had no one-timer value"
        assert ot is not None and abs(ot - sec_val) < 1e-9, (
            f"rank {rank} {name}: enriched one_time={ot} != SEC-confirmed {sec_val}")
        sec_norm = SEC_NORMALIZED_PCT[rank]
        if sec_norm is not None:
            # Tenet / CYH: a material one-timer -> use the SEC pull's own normalized margin
            normalized = round(float(sec_norm), 1)
            source = "SEC-confirmed normalized margin"
        else:
            # HCA / UHS: SEC scan found NO material operating one-timer (impact "none")
            assert ot == 0.0, f"rank {rank}: expected one_time=0 when SEC impact is 'none'"
            normalized = round(mar, 1)
            source = "SEC-scanned, no material one-timer (=reported)"
    else:
        # 36 non-FP systems: NOT independently scanned -> no identified one-timer.
        # normalized = stated margin (authoritative); do NOT recompute from rounded revenue.
        assert ot is None, (f"rank {rank} {name}: unexpected one_time={ot!r} on a non-SEC row "
                            f"(only the 4 FPs should carry a one-timer)")
        normalized = round(mar, 1)
        source = "not scanned (no SEC filing) -> normalized = reported (assumption-limited)"

    r[OWNED_COL] = f"{normalized:.1f}"
    detail.append({
        "rank": rank, "system_name": name,
        "op_margin_pct": mar,
        "one_time_items_musd": ot_raw if ot_raw != '' else None,
        "one_time_source": source,
        "op_margin_q1_normalized_pct": normalized,
        "delta_pp": round(normalized - mar, 1),
        "reporting_period": period,
    })

# ---------------------------------------------------------------- (D) integrity assertions
assert set(by_key) == keys_before, "JOIN KEYS CHANGED during P3 normalize"
assert len(by_key) == 40
for k in by_key:
    for c in NON_OWNED_COLS:
        assert by_key[k][c] == snapshot_before[k][c], \
            f"NON-OWNED COLUMN ALTERED: {k} {c}: {snapshot_before[k][c]!r} -> {by_key[k][c]!r}"
# every row now has a normalized value
assert all(str(r[OWNED_COL]).strip() != '' for r in by_key.values()), "a normalized cell is empty"

# spot-check the headline numbers against the spec / SEC pulls
spot = {d['rank']: d for d in detail}
assert abs(spot[1]['op_margin_q1_normalized_pct'] - 16.4) < 0.05, "Tenet normalized != 16.4"
assert abs(spot[6]['op_margin_q1_normalized_pct'] - 6.4) < 0.05, "CYH normalized != 6.4"
assert abs(spot[2]['op_margin_q1_normalized_pct'] - 12.0) < 0.05, "HCA normalized != 12.0"
assert abs(spot[3]['op_margin_q1_normalized_pct'] - 11.2) < 0.05, "UHS normalized != 11.2"

# ---------------------------------------------------------------- (E) re-rank (before vs after)
# Before = seed op_margin_pct order (= current rank). After = sort by normalized desc, ties broken
# by original rank (stable) so the comparison is deterministic.
before = sorted(detail, key=lambda d: (-d['op_margin_pct'], d['rank']))
after = sorted(detail, key=lambda d: (-d['op_margin_q1_normalized_pct'], d['rank']))
for i, d in enumerate(before, 1):
    d['rank_before'] = i
for i, d in enumerate(after, 1):
    d['rank_after'] = i
# rank_before should equal the seed rank (sanity)
for d in detail:
    assert d['rank_before'] == d['rank'], (
        f"rank_before {d['rank_before']} != seed rank {d['rank']} for {d['system_name']} "
        f"(seed not in margin order?)")
rank_after_by_key = {(d['rank'], d['system_name']): d['rank_after'] for d in detail}
for d in detail:
    d['rank_change'] = d['rank_before'] - d['rank_after']  # +ve = moved up; -ve = moved down

# ---------------------------------------------------------------- (F) write back (preserve col order)
out = [by_key[k] for k in sorted(by_key)]
with open(ENRICHED, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=COLUMNS)
    w.writeheader()
    for r in out:
        w.writerow(r)

# ---------------------------------------------------------------- (G) report
print(f"WROTE {ENRICHED}")
print(f"rows={len(out)} cols={len(COLUMNS)} keys_unchanged={set(by_key)==keys_before} "
      f"normalized_filled={sum(1 for r in out if str(r[OWNED_COL]).strip()!='')}/40")

print("\n=== CONFIRMED ONE-TIME ITEMS STRIPPED (operating-margin-affecting; SEC primary) ===")
for rk in (1, 2, 3, 6):
    d = spot[rk]
    print(f"  #{rk:>2} {d['system_name']:<28} one_time={str(d['one_time_items_musd']):<5} "
          f"reported={d['op_margin_pct']:>5}%  normalized={d['op_margin_q1_normalized_pct']:>5}%  "
          f"delta={d['delta_pp']:+.1f}pp")

print("\n=== BEFORE/AFTER RE-RANK (rows that MOVED) ===")
print(f"  {'sys':<28} {'rep%':>6} {'norm%':>6} {'before':>7} {'after':>6} {'move':>6}")
moved = [d for d in sorted(detail, key=lambda x: x['rank_after']) if d['rank_change'] != 0]
for d in moved:
    arrow = f"{d['rank_change']:+d}"
    print(f"  {d['system_name']:<28} {d['op_margin_pct']:>6} "
          f"{d['op_margin_q1_normalized_pct']:>6} {d['rank_before']:>7} {d['rank_after']:>6} {arrow:>6}")
if not moved:
    print("  (no rank changes)")

print("\n=== TENET FOCUS ===")
t = spot[1]
print(f"  Tenet reported 24.1% (rank {t['rank_before']}) -> normalized "
      f"{t['op_margin_q1_normalized_pct']}% (rank {t['rank_after']}); "
      f"dropped {t['rank_change']*-1 if t['rank_change']<0 else t['rank_change']} place(s) "
      f"({t['rank_before']} -> {t['rank_after']}).")

print("\n=== DERIVED-PERIOD SYSTEMS (flag carried in SEED reporting_period; margins are derived 3-mo) ===")
for d in detail:
    if d['reporting_period'] == 'derived_3mo':
        print(f"  #{d['rank']:>2} {d['system_name']:<28} reported={d['op_margin_pct']}%  "
              f"normalized={d['op_margin_q1_normalized_pct']}%  period={d['reporting_period']}")

# ---------------------------------------------------------------- (H) machine-readable report
report = {
    "rows": len(out),
    "cols": len(COLUMNS),
    "keys_unchanged": set(by_key) == keys_before,
    "owned_column": OWNED_COL,
    "normalized_filled": sum(1 for r in out if str(r[OWNED_COL]).strip() != ''),
    "normalization_rule": ("normalized = stated op_margin_pct adjusted ONLY for a CONFIRMED one-timer. "
                           "For the 4 SEC for-profits with a material one-timer, adopt the SEC pull's own "
                           "normalized margin (Tenet 16.4% = $883M/$5,368M ex-$413M Conifer; CYH 6.4% = "
                           "$191M/$2,965M ex-$90M impairment/gain net). HCA/UHS: no material operating "
                           "one-timer -> normalized = reported. Other 36 (no SEC filing, not scanned) -> "
                           "normalized = stated margin (authoritative; NOT recomputed from rounded revenue, "
                           "to avoid reintroducing rounding/reconciliation noise e.g. Banner's +0.79pp)."),
    "confirmed_one_timers": {
        "1_Tenet": {"one_time_musd": 413, "reported_pct": 24.1, "normalized_pct": spot[1]['op_margin_q1_normalized_pct'], "source": "SEC THC 10-Q + 8-K (Conifer/CommonSpirit)"},
        "2_HCA": {"one_time_musd": 0, "reported_pct": 12.0, "normalized_pct": spot[2]['op_margin_q1_normalized_pct'], "source": "SEC HCA 10-Q (no material operating one-timer)"},
        "3_UHS": {"one_time_musd": 0, "reported_pct": 11.2, "normalized_pct": spot[3]['op_margin_q1_normalized_pct'], "source": "SEC UHS 10-Q (no material operating one-timer)"},
        "6_CYH": {"one_time_musd": 90, "reported_pct": 9.5, "normalized_pct": spot[6]['op_margin_q1_normalized_pct'], "source": "SEC CYH 10-Q (impairment-and-gain-on-sale net)"},
    },
    "tenet_rerank": {"reported_pct": 24.1, "rank_before": spot[1]['rank_before'],
                     "normalized_pct": spot[1]['op_margin_q1_normalized_pct'], "rank_after": spot[1]['rank_after']},
    "moved_rows": [
        {"system": d['system_name'], "reported_pct": d['op_margin_pct'],
         "normalized_pct": d['op_margin_q1_normalized_pct'],
         "rank_before": d['rank_before'], "rank_after": d['rank_after'], "rank_change": d['rank_change']}
        for d in moved
    ],
    "derived_3mo_systems": [
        {"rank": d['rank'], "system": d['system_name'], "normalized_pct": d['op_margin_q1_normalized_pct']}
        for d in detail if d['reporting_period'] == 'derived_3mo'
    ],
    "limitation": ("Only the 4 for-profits (THC/HCA/UHS/CYH) were scanned for one-timers (SEC "
                   "filings). The 36 non-FP systems were NOT independently scanned (no SEC filing; "
                   "CMS/AHRQ do not surface quarterly one-timers; Becker's CDN=403). For them "
                   "normalized=reported is an assumption-limited value, not a confirmed-clean margin."),
}
with open("/tmp/p3_normalize_report.json", "w") as f:
    json.dump(report, f, indent=2)
print("\nreport -> /tmp/p3_normalize_report.json")
