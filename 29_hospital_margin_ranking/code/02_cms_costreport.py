#!/usr/bin/env python3
"""
Issue #29 — Phase 2, CMS Hospital Provider Cost Report (HCRIS) payer/case-mix layer.

Per spec section 7.2 + contracts.md section 4 (stage "P2 CMS-CR"):
  - Source = CMS "Hospital Provider Cost Report" PUF, latest final year (FY2023),
    ONE ROW PER CCN, downloaded from data.cms.gov (NOT the raw relational HCRIS).
  - Filter the national PUF to our systems' CCNs (crosswalk/system_id_map.csv).
  - Save the per-CCN extract to data/raw/cms_costreport_extract.csv.
  - Aggregate to SYSTEM level: pct_medicare_days, pct_medicaid_days, pct_other_days
    (Worksheet S-3 Part I, line 14 days), case_mix_index, dsh_pct,
    uncompensated_care_musd.  Set payer_status per system (ok/partial/not_obtained).

ZERO FABRICATION (contracts.md section 0): every value traces to the downloaded
PUF row. CMI is NOT present in this PUF (verified against the official data
dictionary) -> case_mix_index is left EMPTY for every system (not reconstructed).
Missing CCNs are reported, never imputed.

OWNS ONLY (contracts.md section 4):
  - data/raw/cms_costreport_extract.csv   (the per-CCN filtered extract)
  - appends rows to data/raw/SOURCES.md    (provenance, shared-append per section 6)
  - returns the system-level payer columns + payer_status (does NOT write
    enriched_systems.csv -- that is the P2-merge agent's file).

Field mapping (verbatim from data/raw/cms_hcr_data_dictionary.pdf):
  Total Days Title XVIII  -> Medicare days   (S3-Part1-Line-14-Column-6)
  Total Days Title XIX    -> Medicaid days   (S3-Part1-Line-14-Column-7)
  Total Days Title V      -> CHIP/Title-V days (S3-Part1-Line-14-Column-5; folds to "other")
  Total Days (V+XVIII+XIX+Unknown) -> total inpatient days, all classes
                                       (S3-Part1-Line-14-Column-8)
  Allowable DSH Percentage-> dsh_pct          (E-Part1-Line-33-Column-1; stored as
                                               a fraction in the PUF -> x100 for %)
  Cost of Uncompensated Care -> uncompensated_care_musd primary
                                (S10-Line-30-Column-1, "total cost of non-Medicare
                                 uncompensated care"); /1e6 for $M
  Total Unreimbursed and Uncompensated Care -> carried as a broader companion
                                (S10-Line-31-Column-1)

pct_other_days = (total - Medicare - Medicaid) / total  -> captures private +
Title V + unknown payers (data dictionary: private-insurance days are the residual
of total minus CHIP+Medicare+Medicaid).
"""
import csv
import os
from collections import defaultdict
from datetime import datetime

BASE = "/Users/mgc50/Dropbox/1. Worked On FILES/(28) Vitals&Vars/issues/29_hospital_margin_ranking"
PUF = os.path.join(BASE, "data/raw/CostReport_2023_Final.csv")
XWALK = os.path.join(BASE, "crosswalk/system_id_map.csv")
EXTRACT = os.path.join(BASE, "data/raw/cms_costreport_extract.csv")

# Columns kept in the per-CCN extract (source-traceable subset of the 117-col PUF).
KEEP_COLS = [
    "Provider CCN", "Hospital Name", "State Code", "Provider Type",
    "CCN Facility Type", "Type of Control",
    "Fiscal Year Begin Date", "Fiscal Year End Date",
    "Total Days Title V", "Total Days Title XVIII", "Total Days Title XIX",
    "Total Days (V + XVIII + XIX + Unknown)",
    "Number of Beds",
    "Allowable DSH Percentage",
    "Cost of Charity Care", "Total Bad Debt Expense",
    "Cost of Uncompensated Care", "Total Unreimbursed and Uncompensated Care",
]
TOTAL_DAYS = "Total Days (V + XVIII + XIX + Unknown)"
MCARE = "Total Days Title XVIII"
MCAID = "Total Days Title XIX"


def fnum(s):
    s = (s or "").strip().strip('"').replace(",", "")
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def pdate(s):
    s = (s or "").strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None


def norm_ccn(x):
    x = (x or "").strip().strip('"')
    return x.zfill(6) if x else ""


def period_len(r):
    b, e = pdate(r["Fiscal Year Begin Date"]), pdate(r["Fiscal Year End Date"])
    return (e - b).days if (b and e) else -1


def main():
    # --- load crosswalk: CCN -> (rank, system_name); also ordered system list ---
    ccn_to_sys = {}
    systems = []
    sys_ccns = defaultdict(list)
    with open(XWALK, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rank, name = int(r["rank"]), r["system_name"]
            systems.append((rank, name))
            for c in r["ccn_list"].split(";"):
                c = c.strip()
                if c:
                    ccn_to_sys[c] = (rank, name)
                    sys_ccns[(rank, name)].append(c)

    # --- load PUF; dedup to one row per CCN (longest fiscal period, then latest FYE) ---
    with open(PUF, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        puf_rows = list(rdr)
    by = defaultdict(list)
    for r in puf_rows:
        by[norm_ccn(r["Provider CCN"])].append(r)
    chosen = {}
    for ccn, rs in by.items():
        rs.sort(key=lambda r: (period_len(r), pdate(r["Fiscal Year End Date"]) or datetime.min),
                reverse=True)
        chosen[ccn] = rs[0]

    # --- write per-CCN extract (only our CCNs that exist in the PUF) ---
    out_cols = ["rank", "system_name"] + KEEP_COLS
    n_written = 0
    with open(EXTRACT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(out_cols)
        for c in sorted(ccn_to_sys):
            if c not in chosen:
                continue
            r = chosen[c]
            rank, name = ccn_to_sys[c]
            row = [rank, name] + [r.get(col, "") for col in KEEP_COLS]
            w.writerow(row)
            n_written += 1
    print(f"extract rows written: {n_written} (of {len(ccn_to_sys)} crosswalk CCNs)")

    # --- aggregate to system level ---
    agg = []
    for (rank, name) in systems:
        ccns = sys_ccns[(rank, name)]
        n_total = len(ccns)
        n_matched = sum(1 for c in ccns if c in chosen)
        # day sums (only CCNs with a non-null total-days value contribute)
        s_total = s_mcare = s_mcaid = 0.0
        n_day_ccns = 0
        ucc = 0.0
        ucc_broad = 0.0
        n_ucc = 0
        # day-weighted DSH (weight by total days; only CCNs reporting both)
        dsh_num = dsh_den = 0.0
        n_dsh = 0
        for c in ccns:
            if c not in chosen:
                continue
            r = chosen[c]
            td = fnum(r[TOTAL_DAYS])
            mc = fnum(r[MCARE])
            md = fnum(r[MCAID])
            if td is not None and td > 0:
                s_total += td
                s_mcare += (mc or 0.0)
                s_mcaid += (md or 0.0)
                n_day_ccns += 1
                dsh = fnum(r["Allowable DSH Percentage"])
                if dsh is not None:
                    dsh_num += dsh * td
                    dsh_den += td
                    n_dsh += 1
            u = fnum(r["Cost of Uncompensated Care"])
            if u is not None:
                ucc += u
                n_ucc += 1
            ub = fnum(r["Total Unreimbursed and Uncompensated Care"])
            if ub is not None:
                ucc_broad += ub

        if s_total > 0:
            pct_mcare = round(100.0 * s_mcare / s_total, 1)
            pct_mcaid = round(100.0 * s_mcaid / s_total, 1)
            pct_other = round(100.0 * (s_total - s_mcare - s_mcaid) / s_total, 1)
        else:
            pct_mcare = pct_mcaid = pct_other = ""

        dsh_pct = round(100.0 * dsh_num / dsh_den, 2) if dsh_den > 0 else ""
        ucc_musd = round(ucc / 1e6, 1) if n_ucc > 0 else ""
        ucc_broad_musd = round(ucc_broad / 1e6, 1) if n_ucc > 0 else ""

        day_cov = (n_day_ccns / n_total) if n_total else 0.0
        # status: ok if we matched >=90% of CCNs AND have day data on >=90%;
        # partial if we have some day data but coverage is materially incomplete;
        # not_obtained if no day data at all.
        if n_day_ccns == 0 or s_total == 0:
            status = "not_obtained"
        elif (n_matched / n_total) >= 0.90 and day_cov >= 0.90:
            status = "ok"
        else:
            status = "partial"

        agg.append({
            "rank": rank, "system_name": name,
            "n_ccn_total": n_total, "n_ccn_matched": n_matched,
            "n_ccn_with_days": n_day_ccns,
            "day_coverage_pct": round(100.0 * day_cov, 1),
            "total_inpatient_days": int(s_total) if s_total else "",
            "pct_medicare_days": pct_mcare,
            "pct_medicaid_days": pct_mcaid,
            "pct_other_days": pct_other,
            "case_mix_index": "",  # NOT in this PUF -> not_obtained, never fabricated
            "dsh_pct": dsh_pct,
            "n_ccn_with_dsh": n_dsh,
            "uncompensated_care_musd": ucc_musd,
            "uncomp_care_broad_musd": ucc_broad_musd,
            "n_ccn_with_ucc": n_ucc,
            "payer_status": status,
        })

    # print a compact system-level summary
    hdr = ["rank", "system_name", "n_ccn_matched", "n_ccn_total", "day_coverage_pct",
           "pct_medicare_days", "pct_medicaid_days", "pct_other_days",
           "dsh_pct", "uncompensated_care_musd", "case_mix_index", "payer_status"]
    print("\t".join(hdr))
    for a in agg:
        print("\t".join(str(a[k]) for k in hdr))

    return agg


if __name__ == "__main__":
    main()
