# Issue #29 Toolkit: What a Viral Hospital Margin Ranking Actually Measures

The open dataset and reproducible pipeline behind **Vitals & Variables Issue #29**. A viral ranking sorted 40 large U.S. health systems by Q1 2026 operating margin, from +24.1% down to -4.5%. This toolkit lets you re-cut that 28.6-point spread yourself and see what it actually measures: ownership and tax status, the health-plan premium denominator, safety-net and payer exposure, and one-time accounting items. It is a structure map, not a leaderboard.

## What's in here

- **`data/enriched_systems.csv`** - the master dataset: 40 systems by 38 columns (financials, ownership/archetype, scale, payer mix, digital maturity, geography). Start here.
- `data/q1_2026_margins.csv` - the corrected Q1 2026 financials (the seed).
- `data/phase0_classification.csv` - ownership / archetype / faith / health-plan classifications.
- `data/system_id_map.csv` - crosswalk: Becker's name to AHRQ system ID to CMS CCNs, with a `boundary_match` quality flag.
- `analysis_summary.md` - the H1 to H9 findings (the numbers behind the article).
- `SOURCES.md` - every external source with its URL and retrieval date.
- `code/` - the reference pipeline (joins, normalization, analysis, charts). See the note below.
- `charts/` - four headline figures (PNG, no logos).

## The dataset (key columns)

- **Financials:** `op_revenue_musd`, `op_income_musd`, `op_margin_pct` (Q1 2026, USD millions); `op_margin_q1_normalized_pct` (net of one-time items); `one_time_items_musd`; `reporting_period`.
- **Ownership and type:** `ownership` (for-profit / nonprofit), `faith_tradition`, `archetype`, `plan_materiality` (none / minor / material), `academic_flag`, `teaching_intensity`.
- **Scale:** `total_acute_beds`, `hospital_count`, `multistate_flag`, `annual_total_revenue_musd`, `ahrq_system_id`, `boundary_match`.
- **Payer / case mix (CMS cost report, FY2023):** `pct_medicare_days`, `pct_medicaid_days`, `pct_other_days`, `dsh_pct`, `uncompensated_care_musd`. (`case_mix_index` is not in the CMS PUF, so it is intentionally blank.)
- **Digital maturity:** `cms_pi_metric` (CMS Promoting Interoperability share, CY2024), `chime_dhmw_level`, `newsweek_smart_rank`, `himss_emram7_flag`.
- **Geography / policy:** `census_region`, `medicaid_expansion_hq`, `national_operator_flag`, `con_law_state`.

## Headline findings (descriptive)

- Tax status sorts the extremes: the 4 for-profits average **14.2%** vs **2.8%** for the 36 nonprofits, and all 4 sit in the top 6.
- Strip Tenet's **$413M one-time Conifer gain** and its margin falls from 24.1% to **16.4%**; the headline 28.6-point spread shrinks to **20.9**.
- Margin correlates with safety-net burden (**DSH at -0.72**) but with Medicaid-day share at about **zero** - measure safety-net load with DSH, not Medicaid days.
- Scale does not predict margin (**r = 0.11**). Digital maturity does not predict margin (**CMS interoperability r = -0.03**); the three CHIME "Level 10" systems span **+9.3% to -0.9%**.

## How to use it

The dataset is ready as-is: open `data/enriched_systems.csv` and re-rank, filter, or cut by any column. The `code/` scripts are the reference pipeline from the source repo (their paths assume that repo's layout, so treat them as methodology reference rather than turnkey scripts). `code/requirements.txt` lists the Python dependencies.

## Sources

All inputs are free and public: SEC EDGAR (for the 4 for-profits), the CMS Hospital Provider Cost Report PUF and CMS Promoting Interoperability dataset, the AHRQ Compendium of U.S. Health Systems, KFF, NCSL, CHIME, Newsweek, HIMSS, and Becker's Hospital Review per-system Q1 2026 coverage. Full URLs and retrieval dates are in `SOURCES.md`.

## Caveats

Descriptive and hypothesis-generating only: n = 40, a curated (non-random) list, with two systems reporting derived three-month figures. Report effect sizes and ranges, not p-values. Structural attributes (payer mix, beds, interoperability) are point-in-time (FY2023 / CY2024 / the 2023 AHRQ edition) and represent stable structure, not 2026 financials. One-time items were sourced only for the 4 for-profits, so the normalized spread is a lower bound. See `analysis_summary.md` for the full assumptions.

---

Part of the **Vitals & Variables** LinkedIn Newsletter, Issue #29.
