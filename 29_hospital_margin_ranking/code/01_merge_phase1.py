#!/usr/bin/env python3
"""
Issue #29 — Phase 1 merge.
Creates data/processed/enriched_systems.csv per contracts.md section 2.

Starts from the seed (q1_2026_margins.csv + phase0_classification.csv joined on
rank+system_name), adds AHRQ structural columns (via crosswalk/system_id_map.csv ->
ahrq_system_2023.csv), and the five reference flags (ref_*.csv).

ZERO FABRICATION: every non-seed value traces to a downloaded file in data/raw/.
Where a value cannot be honestly attributed (BayCare's shared-parent AHRQ scale),
the cell is left EMPTY (not_obtained), never reconstructed.

Owns ONLY: data/processed/enriched_systems.csv  (per contracts.md section 4, P1 merge)
"""
import csv
import sys

BASE = "/Users/mgc50/Dropbox/1. Worked On FILES/(28) Vitals&Vars/issues/29_hospital_margin_ranking"

# ---------------------------------------------------------------- load seed
margins = {}
with open(f"{BASE}/data/processed/q1_2026_margins.csv", newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        margins[(int(row['rank']), row['system_name'])] = row

classif = {}
with open(f"{BASE}/data/processed/phase0_classification.csv", newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        classif[(int(row['rank']), row['system_name'])] = row

# join keys must match exactly on rank+system_name
mkeys, ckeys = set(margins), set(classif)
assert mkeys == ckeys, f"SEED KEY MISMATCH: only in margins={mkeys-ckeys}; only in classif={ckeys-mkeys}"
assert len(margins) == 40, f"expected 40 seed rows, got {len(margins)}"

# ---------------------------------------------------------------- crosswalk
xwalk = {}
with open(f"{BASE}/crosswalk/system_id_map.csv", newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        xwalk[(int(row['rank']), row['system_name'])] = row
assert set(xwalk) == mkeys, "CROSSWALK keys do not match seed keys"

# ---------------------------------------------------------------- AHRQ system file (cp1252)
ahrq = {}
with open(f"{BASE}/data/raw/ahrq_system_2023.csv", newline='', encoding='cp1252') as f:
    for row in csv.DictReader(f):
        ahrq[row['health_sys_id']] = row

# ---------------------------------------------------------------- reference tables
def load_ref(fname, key_col):
    d = {}
    with open(f"{BASE}/data/raw/{fname}", newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            d[row[key_col]] = row
    return d

ref_kff   = load_ref("ref_kff_expansion.csv", "state")          # keyed by full state name
ref_ncsl  = load_ref("ref_ncsl_con.csv", "state_abbr")          # keyed by state abbr
ref_chime = load_ref("ref_chime_dhmw.csv", "system_name")
ref_news  = load_ref("ref_newsweek_smart.csv", "system_name")
ref_himss = load_ref("ref_himss_emram7.csv", "system_name")

# state abbr -> full name (for KFF join from hq_state)
STATE_FULL = {
    'AL':'Alabama','AK':'Alaska','AZ':'Arizona','AR':'Arkansas','CA':'California','CO':'Colorado',
    'CT':'Connecticut','DE':'Delaware','DC':'District of Columbia','FL':'Florida','GA':'Georgia',
    'HI':'Hawaii','ID':'Idaho','IL':'Illinois','IN':'Indiana','IA':'Iowa','KS':'Kansas','KY':'Kentucky',
    'LA':'Louisiana','ME':'Maine','MD':'Maryland','MA':'Massachusetts','MI':'Michigan','MN':'Minnesota',
    'MS':'Mississippi','MO':'Missouri','MT':'Montana','NE':'Nebraska','NV':'Nevada','NH':'New Hampshire',
    'NJ':'New Jersey','NM':'New Mexico','NY':'New York','NC':'North Carolina','ND':'North Dakota',
    'OH':'Ohio','OK':'Oklahoma','OR':'Oregon','PA':'Pennsylvania','RI':'Rhode Island','SC':'South Carolina',
    'SD':'South Dakota','TN':'Tennessee','TX':'Texas','UT':'Utah','VT':'Vermont','VA':'Virginia',
    'WA':'Washington','WV':'West Virginia','WI':'Wisconsin','WY':'Wyoming',
}

OWN_MAP = {'1':'nonprofit','2':'church-operated','3':'public-government','5':'for-profit'}
TEACH_MAP = {'0':'nonteaching','1':'minor teaching','2':'major teaching'}

# Rows whose AHRQ id is a SHARED-PARENT and therefore whose AHRQ *scale* columns
# describe the parent, NOT the Becker's reporting entity. For these we keep
# ahrq_system_id + boundary_match but leave system-scale AHRQ numerics EMPTY
# (cannot honestly attribute the parent's national totals to a subset entity).
# Determined empirically: BayCare (#4) shares HSI00001106 with Trinity (#29).
SHARED_PARENT_NULL_SCALE = set()  # filled after we detect shared ids below

# detect shared AHRQ ids among DIFFERENT Becker entities
from collections import defaultdict
id_to_ranks = defaultdict(list)
for (rank, name), x in xwalk.items():
    id_to_ranks[x['ahrq_system_id']].append((rank, x['boundary_match']))

# Tenet one-time item: $413M Conifer, SEED-noted + Phase-0 SEC-8-K verified
# (data/raw/phase0_verify/sec_THC_8k_q1_2026_earnings.htm). Contract tags
# one_time_items_musd as SEC/SEED and names Tenet ~413 as the canonical example.
ONE_TIME = {1: '413'}  # only Tenet; other SEC one-timers are P2-SEC's to fill

# ---------------------------------------------------------------- column order (contracts.md s2)
COLUMNS = [
    # identity & financials
    'rank','system_name','hq_city','hq_state',
    'op_revenue_musd','op_income_musd','op_margin_pct','reporting_period',
    'one_time_items_musd','op_margin_q1_normalized_pct',
    # ownership & archetype
    'ownership','faith_tradition','archetype','plan_materiality',
    'academic_flag','teaching_intensity',
    # scale
    'ahrq_system_id','total_acute_beds','hospital_count','multistate_flag',
    'annual_total_revenue_musd','boundary_match',
    # payer / case mix (P2)
    'pct_medicare_days','pct_medicaid_days','pct_other_days','case_mix_index',
    'dsh_pct','uncompensated_care_musd','payer_status',
    # digital / AI maturity
    'cms_pi_metric','chime_dhmw_level','newsweek_smart_rank','himss_emram7_flag','digital_status',
    # geography / policy
    'census_region','medicaid_expansion_hq','national_operator_flag','con_law_state',
]

mismatches = []          # (rank, system, field, detail) for notes.md mismatch log
fill_counts = {c: 0 for c in COLUMNS}
out_rows = []

for rank in range(1, 41):
    # find the seed key with this rank
    key = next(k for k in mkeys if k[0] == rank)
    name = key[1]
    m = margins[key]; c = classif[key]; x = xwalk[key]
    sid = x['ahrq_system_id']
    a = ahrq[sid]
    bmatch = x['boundary_match']

    row = {col: '' for col in COLUMNS}

    # ---- identity & financials (SEED, do not alter)
    row['rank'] = rank
    row['system_name'] = name
    row['hq_city'] = m['hq_city']
    row['hq_state'] = m['hq_state']
    row['op_revenue_musd'] = m['op_revenue_musd']
    row['op_income_musd'] = m['op_income_musd']
    row['op_margin_pct'] = m['op_margin_pct']
    row['reporting_period'] = m['reporting_period']
    row['one_time_items_musd'] = ONE_TIME.get(rank, '')     # Tenet only; else P2-SEC
    row['op_margin_q1_normalized_pct'] = ''                  # P3 derive

    # ---- ownership & archetype (SEED authoritative; AHRQ confirm + log mismatch)
    row['ownership'] = c['ownership']
    row['faith_tradition'] = c['faith_tradition']
    row['archetype'] = c['archetype']
    row['plan_materiality'] = c['plan_materiality']

    ahrq_own_raw = OWN_MAP.get(a['sys_ownership'], a['sys_ownership'])
    is_church = (a['sys_ownership'] == '2')

    # ownership reconciliation (church-operated maps to seed nonprofit)
    ahrq_own_as_seed = 'nonprofit' if ahrq_own_raw == 'church-operated' else ahrq_own_raw
    if ahrq_own_as_seed != c['ownership']:
        mismatches.append((rank, name, 'ownership',
            f"seed={c['ownership']} vs AHRQ sys_ownership={ahrq_own_raw}"))

    # faith reconciliation (seed faith vs AHRQ church-operated flag)
    seed_has_faith = c['faith_tradition'] in ('Catholic', 'Adventist')
    if seed_has_faith != is_church:
        if rank == 4:  # BayCare shared-parent artifact
            mismatches.append((rank, name, 'faith_tradition',
                f"seed={c['faith_tradition']} (secular) vs AHRQ church-operated=True -- BOUNDARY ARTIFACT: "
                f"BayCare has no standalone AHRQ system; folded under Trinity parent {sid} (boundary_match=subset). "
                f"Seed value retained; AHRQ flag reflects Trinity, not BayCare."))
        else:
            mismatches.append((rank, name, 'faith_tradition',
                f"seed={c['faith_tradition']} vs AHRQ church-operated={is_church} [bmatch={bmatch}]"))

    # plan_materiality reconciliation (seed scale vs AHRQ binary sys_anyins_product)
    ins = a['sys_anyins_product']
    plan = c['plan_materiality']
    if plan in ('material', 'minor') and ins == '0':
        mismatches.append((rank, name, 'plan_materiality',
            f"seed={plan} but AHRQ sys_anyins_product=0 (no plan/JV flagged) [bmatch={bmatch}]"))
    elif plan == 'none' and ins == '1':
        mismatches.append((rank, name, 'plan_materiality',
            f"seed=none but AHRQ sys_anyins_product=1 (AHRQ flags any insurer ownership/JV/partnership;"
            f" broader than seed materiality) [bmatch={bmatch}]"))

    # academic_flag (AHRQ): system includes >=1 major teaching hospital
    # teaching_intensity (AHRQ): sys_teachint label
    null_scale = (rank == 4)  # BayCare shared parent -> AHRQ scale describes Trinity, not BayCare
    if null_scale:
        row['academic_flag'] = ''
        row['teaching_intensity'] = ''
    else:
        row['academic_flag'] = 'Y' if a['sys_incl_majteachhosp'] == '1' else 'N'
        row['teaching_intensity'] = TEACH_MAP.get(a['sys_teachint'], '')

    # ---- scale (AHRQ)
    row['ahrq_system_id'] = sid                       # legitimate even for BayCare (documented shared parent)
    row['boundary_match'] = bmatch
    if null_scale:
        # leave beds/hospital_count/multistate/revenue EMPTY (not_obtained):
        # the AHRQ row is Trinity's national system, not BayCare's FL subset.
        row['total_acute_beds'] = ''
        row['hospital_count'] = ''
        row['multistate_flag'] = ''
        row['annual_total_revenue_musd'] = ''
    else:
        row['total_acute_beds'] = a['sys_beds']                       # sys_beds = acute-care beds (HCRIS)
        row['hospital_count'] = a['hosp_cnt']                         # all-type hospital count
        row['multistate_flag'] = 'Y' if a['sys_multistate'] in ('2', '3') else 'N'
        # annual_total_revenue_musd = AHRQ NET patient revenue (acute hospitals), $ -> $M.
        # NOTE field-name inversion: CSV `hos_net_revenue` IS net patient revenue
        # (techdoc "Total net patient revenue"); CSV `hos_total_revenue` is GROSS charges.
        net = a.get('hos_net_revenue', '').strip()
        if net not in ('', '.', 'NA'):
            try:
                row['annual_total_revenue_musd'] = f"{float(net)/1e6:.1f}"
            except ValueError:
                row['annual_total_revenue_musd'] = ''
        else:
            row['annual_total_revenue_musd'] = ''

    # ---- payer / case mix (P2 -- leave empty, status not_obtained)
    row['payer_status'] = 'not_obtained'

    # ---- digital / AI maturity
    row['cms_pi_metric'] = ''                                          # P2 (CMS-PI)
    row['chime_dhmw_level'] = ref_chime[name]['chime_dhmw_level']      # REF
    nw = ref_news[name]['newsweek_smart_rank'].strip()
    row['newsweek_smart_rank'] = nw                                   # REF (blank = unranked / not in 350)
    row['himss_emram7_flag'] = ref_himss[name]['himss_emram7']        # REF (Y/unknown)
    # digital_status: partial (REF flags present; cms_pi pending P2)
    row['digital_status'] = 'partial'

    # ---- geography / policy
    row['census_region'] = c['census_region']                         # SEED
    row['medicaid_expansion_hq'] = c['medicaid_expansion_hq']         # SEED (KFF-reconciled upstream)
    row['national_operator_flag'] = c['national_operator_flag']      # SEED
    # con_law_state from NCSL ref, joined on hq_state abbr
    st = m['hq_state']
    row['con_law_state'] = ref_ncsl[st]['con_law'] if st in ref_ncsl else ''

    out_rows.append(row)
    for col in COLUMNS:
        if str(row[col]).strip() != '':
            fill_counts[col] += 1

# ---------------------------------------------------------------- write
out_path = f"{BASE}/data/processed/enriched_systems.csv"
with open(out_path, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=COLUMNS)
    w.writeheader()
    for row in out_rows:
        w.writerow(row)

print(f"WROTE {out_path}")
print(f"rows={len(out_rows)} cols={len(COLUMNS)}")

# ---------------------------------------------------------------- fill report
print("\n=== FILL RATES (n=40) ===")
for col in COLUMNS:
    print(f"  {col:<32} {fill_counts[col]:>3}/40")

# ---------------------------------------------------------------- mismatch dump
print("\n=== AHRQ-vs-SEED MISMATCHES ===")
for rank, name, field, detail in mismatches:
    print(f"  #{rank} {name} :: {field} :: {detail}")

# expose for the harness
import json
with open("/tmp/p1_merge_report.json", "w") as f:
    json.dump({
        "rows": len(out_rows),
        "fill_counts": fill_counts,
        "mismatches": [f"#{r} {n} :: {fld} :: {d}" for r,n,fld,d in mismatches],
    }, f, indent=2)
