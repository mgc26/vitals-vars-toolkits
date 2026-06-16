#!/usr/bin/env python3
"""
Issue #29 — Phase 2 merge (P2-merge).

UPDATES data/processed/enriched_systems.csv in place with the three P2 layers:
  (1) Payer / case-mix columns  <- CMS Cost Report aggregation (code/02_cms_costreport.py)
        pct_medicare_days, pct_medicaid_days, pct_other_days,
        case_mix_index (left EMPTY — not in the PUF), dsh_pct,
        uncompensated_care_musd, payer_status
  (2) Digital columns           <- CMS Promoting Interoperability roll-up + already-present REF flags
        cms_pi_metric (now filled), digital_status (upgraded from P1 'partial' to the
        sourced per-system PI-coverage status). chime/newsweek/himss already merged by P1.
  (3) SEC one-time items        <- data/raw/sec_{THC,HCA,UHS,CYH}.json
        one_time_items_musd for the 4 for-profits (Tenet 413 already set by P1; HCA 0; UHS 0; CYH 90).

Keeps all 40 rows, all join keys (rank, system_name), and every column the P1 merge
wrote.  Does NOT touch P3's op_margin_q1_normalized_pct (stays empty here).

ZERO FABRICATION (contracts.md s0): every value traces to a file in data/raw/ already
manifested in data/raw/SOURCES.md (this stage re-downloads nothing).
  - case_mix_index is NOT in the CMS Cost Report PUF -> left EMPTY for all 40 (never reconstructed).
  - Any payer cell with no source days is left EMPTY + payer_status carries the reason.

Owns ONLY: data/processed/enriched_systems.csv (per contracts.md s4, "P2 merge").
Reads (read-only): the P1 enriched CSV, CostReport_2023_Final.csv + crosswalk (via
02_cms_costreport.main()), cms_pi_extract.csv, sec_{THC,HCA,UHS,CYH}.json.
"""
import csv
import json
import importlib.util
import os
import sys

BASE = "/Users/mgc50/Dropbox/1. Worked On FILES/(28) Vitals&Vars/issues/29_hospital_margin_ranking"
ENRICHED = f"{BASE}/data/processed/enriched_systems.csv"

# ---------------------------------------------------------------- (A) load current enriched CSV
with open(ENRICHED, newline='', encoding='utf-8') as f:
    rdr = csv.DictReader(f)
    COLUMNS = list(rdr.fieldnames)
    rows = list(rdr)
assert len(rows) == 40, f"expected 40 rows in enriched, got {len(rows)}"
by_key = {(int(r['rank']), r['system_name']): r for r in rows}
keys_before = set(by_key)

# capture a snapshot of the non-P2 columns so we can prove we didn't alter them
NON_P2_COLS = [c for c in COLUMNS if c not in {
    'pct_medicare_days', 'pct_medicaid_days', 'pct_other_days', 'case_mix_index',
    'dsh_pct', 'uncompensated_care_musd', 'payer_status',
    'cms_pi_metric', 'digital_status',
    'one_time_items_musd',  # P1 set Tenet=413; P2 fills the other 3 for-profits
}]
snapshot_before = {k: {c: by_key[k][c] for c in NON_P2_COLS} for k in by_key}

# ---------------------------------------------------------------- (B) CMS Cost Report payer aggregation
# Import code/02_cms_costreport.py and call main() to get the deterministic per-system agg.
spec = importlib.util.spec_from_file_location("cms_cr", f"{BASE}/code/02_cms_costreport.py")
cms_cr = importlib.util.module_from_spec(spec)
# silence its stdout while we import/run
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    spec.loader.exec_module(cms_cr)
    payer_agg = cms_cr.main()
payer_by_key = {(a['rank'], a['system_name']): a for a in payer_agg}
assert set(payer_by_key) == keys_before, "CMS-CR agg keys do not match enriched keys"

# ---------------------------------------------------------------- (C) CMS PI digital roll-up
pi_by_key = {}
with open(f"{BASE}/data/raw/cms_pi_extract.csv", newline='', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        pi_by_key[(int(r['rank']), r['system_name'])] = r
assert set(pi_by_key) == keys_before, "CMS-PI extract keys do not match enriched keys"

# ---------------------------------------------------------------- (D) SEC one-time items (4 for-profits)
def sec_one_time(path):
    """Pull the contracts-schema one_time_items_musd from a P2-SEC JSON, robust to the
    two layouts present (THC uses one_time_items.one_time_items_musd; HCA/UHS/CYH use
    one_time_items.for_contracts_one_time_items_musd.value or CYH's explicit field)."""
    with open(path, encoding='utf-8') as f:
        j = json.load(f)
    oti = j.get('one_time_items', {})
    # preferred: the explicit contracts-schema recommendation
    fc = oti.get('for_contracts_one_time_items_musd')
    if isinstance(fc, dict) and fc.get('value') is not None:
        return float(fc['value']), j.get('system_name') or j.get('_meta', {}).get('system_name')
    # THC layout: one_time_items_musd at the block top level (the $413M Conifer line)
    if oti.get('one_time_items_musd') is not None:
        return float(oti['one_time_items_musd']), j.get('system_name')
    # CYH layout: the impairment-and-gain-on-sale net embedded in operating income
    if oti.get('impairment_and_gain_on_sale_of_businesses_net_musd') is not None:
        return float(oti['impairment_and_gain_on_sale_of_businesses_net_musd']), j.get('system_name')
    return None, j.get('system_name')

sec_files = {
    1: f"{BASE}/data/raw/sec_THC.json",
    2: f"{BASE}/data/raw/sec_HCA.json",
    3: f"{BASE}/data/raw/sec_UHS.json",
    6: f"{BASE}/data/raw/sec_CYH.json",
}
sec_one_time_by_rank = {}
for rank, path in sec_files.items():
    val, name = sec_one_time(path)
    sec_one_time_by_rank[rank] = (val, name)

# ---------------------------------------------------------------- (E) merge into rows
PI_METRIC_COL = 'cms_pi_metric_all_ccn_den'   # fraction in [0,1] = (CCNs meeting PI) / (ALL system crosswalk CCNs)
PI_MEASURE_NAME = ("Fraction of all system crosswalk CCNs that met the CMS Promoting "
                   "Interoperability criteria (\"Meets criteria for promoting interoperability "
                   "of EHRs\" = Y) for the CY2024 reporting period. Denominator = ALL CCNs in the "
                   "crosswalk (CCNs absent from the PI file or with CEHRT 'Not Available' count as "
                   "did-not-demonstrate), so this is a conservative coverage-aware participation rate, "
                   "NOT a fraction of only the reporting CCNs.")

for k, r in by_key.items():
    rank = k[0]
    # ---- payer / case mix
    p = payer_by_key[k]
    for col in ('pct_medicare_days', 'pct_medicaid_days', 'pct_other_days',
                'dsh_pct', 'uncompensated_care_musd', 'payer_status'):
        r[col] = '' if p[col] == '' else str(p[col])
    r['case_mix_index'] = ''  # NOT in the PUF -> stays empty (not_obtained), never fabricated

    # ---- digital
    pi = pi_by_key[k]
    pim = pi[PI_METRIC_COL].strip()
    r['cms_pi_metric'] = pim if pim != '' else ''
    r['digital_status'] = pi['digital_status'].strip()  # sourced per-system PI-coverage status

    # ---- SEC one-time items (4 for-profits only; leave the 36 nonprofits as P1 left them)
    if rank in sec_one_time_by_rank:
        val, name = sec_one_time_by_rank[rank]
        assert name == k[1], f"SEC json name '{name}' != enriched '{k[1]}' for rank {rank}"
        if val is not None:
            # format: integer if whole, else trimmed float
            r['one_time_items_musd'] = str(int(val)) if float(val).is_integer() else str(val)

# ---------------------------------------------------------------- (F) integrity assertions
# keys + row count unchanged
assert set(by_key) == keys_before, "JOIN KEYS CHANGED during P2 merge"
assert len(by_key) == 40

# non-P2 columns untouched
for k in by_key:
    for c in NON_P2_COLS:
        assert by_key[k][c] == snapshot_before[k][c], \
            f"NON-P2 COLUMN ALTERED: {k} {c}: {snapshot_before[k][c]!r} -> {by_key[k][c]!r}"

# reconciliation re-run: op_income/op_revenue ≈ op_margin (income+margin authoritative; revenue rounded)
recon_flags = []
for k, r in by_key.items():
    rev = float(r['op_revenue_musd']); inc = float(r['op_income_musd']); mar = float(r['op_margin_pct'])
    calc = 100.0 * inc / rev if rev else None
    gap = abs(calc - mar) if calc is not None else None
    if gap is not None and gap > 0.5:
        recon_flags.append((k[0], k[1], round(calc, 2), mar, round(gap, 2)))

# ---------------------------------------------------------------- (G) write back (preserve column order)
out = [by_key[k] for k in sorted(by_key)]
with open(ENRICHED, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=COLUMNS)
    w.writeheader()
    for r in out:
        w.writerow(r)

# ---------------------------------------------------------------- (H) fill report
P2_COLS = ['pct_medicare_days', 'pct_medicaid_days', 'pct_other_days', 'case_mix_index',
           'dsh_pct', 'uncompensated_care_musd', 'payer_status',
           'cms_pi_metric', 'digital_status', 'one_time_items_musd']
fill = {c: sum(1 for r in out if str(r[c]).strip() != '') for c in P2_COLS}

print(f"WROTE {ENRICHED}")
print(f"rows={len(out)} cols={len(COLUMNS)} keys_unchanged={set(by_key)==keys_before}")
print("\n=== P2 FILL RATES (n=40) ===")
for c in P2_COLS:
    print(f"  {c:<28} {fill[c]:>3}/40")

print("\n=== payer_status distribution ===")
from collections import Counter
print("  " + str(dict(Counter(r['payer_status'] for r in out))))
print("=== digital_status distribution ===")
print("  " + str(dict(Counter(r['digital_status'] for r in out))))

print("\n=== one_time_items_musd (non-empty) ===")
for r in out:
    if str(r['one_time_items_musd']).strip() != '':
        print(f"  #{r['rank']:>2} {r['system_name']:<28} {r['one_time_items_musd']}")

print("\n=== RECONCILIATION (gap>0.5pp) ===")
if not recon_flags:
    print("  none (all 40 within +/-0.5pp)")
for rank, name, calc, mar, gap in recon_flags:
    print(f"  #{rank} {name}: calc={calc}% stated={mar}% gap={gap}pp")

print("\n=== NOT-OBTAINED / EMPTY P2 cells ===")
for r in out:
    empties = [c for c in P2_COLS if str(r[c]).strip() == '']
    if empties:
        print(f"  #{r['rank']:>2} {r['system_name']:<28} empty: {empties}")

# expose for the harness
with open("/tmp/p2_merge_report.json", "w") as f:
    json.dump({
        "rows": len(out),
        "cols": len(COLUMNS),
        "keys_unchanged": set(by_key) == keys_before,
        "fill_counts": fill,
        "payer_status": dict(Counter(r['payer_status'] for r in out)),
        "digital_status": dict(Counter(r['digital_status'] for r in out)),
        "reconciliation_flags": [f"#{rk} {nm}: calc={c}% stated={m}% gap={g}pp"
                                 for rk, nm, c, m, g in recon_flags],
        "pi_metric_column_used": PI_METRIC_COL,
        "pi_measure_name": PI_MEASURE_NAME,
        "case_mix_index": "EMPTY for all 40 (not in CMS Cost Report PUF; not fabricated)",
    }, f, indent=2)
print("\nreport -> /tmp/p2_merge_report.json")
