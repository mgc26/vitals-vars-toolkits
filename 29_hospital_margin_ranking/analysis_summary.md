# Issue #29 — Analysis Summary (P3 synthesis memo)

**Phase:** P3 summary · **Date:** 2026-06-16 · **Owner:** P3-summary (writes only `outputs/analysis_summary.md`)
**Inputs (read-only):** `outputs/h1..h9_findings.md`, `outputs/fig1..fig6*.png`, `data/processed/enriched_systems.csv`, `data/raw/SOURCES.md`.
**Purpose:** This memo is the **sole factual basis** the Phase-4 article may draw on. Every number below traces either to a named column in `enriched_systems.csv` (the master dataset, n=40, keyed `rank`,`system_name`) or to a file in `data/raw/` recorded in `SOURCES.md`. No value here was estimated, reconstructed, or filled to make anything reconcile.

**Statistical posture (non-negotiable, per DESIGN.md §6 / spec §11):** n=40, **non-random** (a curated Becker's list), **heterogeneous reporting periods** (2 derived 3-month entries). Everything is **descriptive / hypothesis-generating**. Report effect sizes and ranges; **no p-values, no causal claims.** Words like "sorter," "separates," "predicts," "tracks" are descriptive, not causal. With cells this small (some groups n=2–5), single systems move every statistic and are named throughout.

**Source-verification status (carry from Phase 0 / `notes.md`):** The *individual* Q1-2026 figures are primary-source-confirmed for the systems spot-checked (SEC XBRL for the 4 for-profits; Becker's per-system items + system newsrooms for others). The *umbrella* Becker's article — its exact title and the "24.1% to −4.5%" endpoints — could **not** be independently confirmed (Becker's CDN returns HTTP 403 to fetchers; the exact title returns zero search hits). **Do not cite the umbrella headline as a verified source.** Two specific figures carry open flags (Montefiore floor; Banner revenue) — see §8.

---

## 1. The one-paragraph synthesis

The Becker's "From 24.1% to −4.5%: 40 health systems ranked by Q1 operating margins" is **a structure map, not a leaderboard of operating skill.** The 28.6-percentage-point spread (Tenet +24.1% to Montefiore −4.5%, `op_margin_pct`) is largely explained by four **structural** factors, not by management quality: (1) **ownership / tax status** — the single largest sorter (H1); (2) the **health-plan premium denominator** that mechanically compresses integrated payer-providers' percentage margin (H2); (3) **safety-net / payer exposure**, the axis that splits the academic medical centers (H4); and (4) **accounting artifacts** — one-time items and derived reporting periods that inflate the top of the board (H6). Two things you might expect to be management levers turn out **not** to sort the ranking: **scale** (H7, effectively zero correlation on a like-for-like basis) and **digital/IT maturity** (H9, ≈0 correlation; the most digitally elite cohort in the data already spans a money-loser to a top nonprofit). Geography (Medicaid expansion, H8) is a weak, direction-unreliable covariate. The defensible read: **once you account for structure, the "ranking" largely dissolves.**

---

## 2. Headline numbers (all from `enriched_systems.csv`, recomputed and reconciled)

| Fact | Value | Source column(s) |
|---|---|---|
| Full margin spread | **28.6 pp** (max +24.1% Tenet #1 → min −4.5% Montefiore #40) | `op_margin_pct` |
| Spread after stripping the 2 sourced for-profit one-timers | **20.9 pp** (Tenet → 16.4%; floor unchanged) | `op_margin_q1_normalized_pct` |
| For-profit cohort (n=4) mean margin | **14.20%** | `ownership`,`op_margin_pct` |
| Nonprofit cohort (n=36) mean margin | **2.76%** | `ownership`,`op_margin_pct` |
| For-profit − nonprofit mean gap | **+11.44 pp** | derived from the two rows above |
| For-profit revenue-weighted margin (Σinc/Σrev) | **13.67%** | `op_income_musd`/`op_revenue_musd` |
| Nonprofit revenue-weighted margin (Σinc/Σrev) | **2.81%** | `op_income_musd`/`op_revenue_musd` |
| All-40 mean / median margin | **3.91% / 3.05%** | `op_margin_pct` |
| Ownership composition of the list | 4 for-profit, 36 nonprofit, **0 public-government** | `ownership` |
| All 4 for-profits' ranks | **{1, 2, 3, 6}** — all in the top 6 | `rank`,`ownership` |
| Tenet's one-time Conifer gain | **$413M** (margin effect −7.7 pp: 24.1% → 16.4%) | `one_time_items_musd`; provenance: SEC THC 8-K/10-Q in `SOURCES.md` |

**Reconciliation note (use income + margin, treat revenue as rounded):** Becker's rounds revenue/expenses but reports operating income precisely, so `revenue − expenses ≠ income` for most rows. Per `notes.md` §3, **operating income and margin are authoritative; revenue is rounded.** 39 of 40 rows reconcile (`op_income/op_revenue ≈ op_margin`) within ±0.5pp; the one exception (Banner #19) is flagged in §8.

---

## 3. The four-factor decomposition (the spine of the article)

### Factor 1 — Ownership / tax status is the dominant sorter (H1)
- For-profit mean **14.20%** vs nonprofit **2.76%** — a **+11.44 pp** gap; revenue-weighted gap **+10.86 pp** (13.67% vs 2.81%). Rank-based effect size **Cliff's δ = 0.972** (142 of 144 for-profit×nonprofit pairs favor the for-profit) — the preferred summary given for-profit n=4. (`h1_findings.md` §1–2)
- **All 4 for-profits sit in the top 6** (ranks 1,2,3,6). **But it is not a clean partition:** two nonprofits — **BayCare #4 (+10.6%)** and **NewYork-Presbyterian #5 (+9.6%)** — outrank the lowest for-profit, **Community Health Systems #6 (+9.5%)**. The honest framing is "tax status sorts the **extremes** / is the **single largest** sorter," **not** "every for-profit beats every nonprofit." (`h1_findings.md` §4)
- The gap **survives normalization** (strip Tenet's Conifer gain + CHS's one-timer): for-profit mean falls 14.20% → 11.50%, gap narrows to **+8.74 pp** but does not reverse. (`h1_findings.md` §5)
- **Interpretive caution:** this effect **conflates** tax treatment, business mix, capital structure, and (for some nonprofits) the plan denominator. H1 is the headline split; H2–H9 decompose *why*. Do **not** present the gap as "for-profits are better operators." (`h1_findings.md` §6)

### Factor 2 — The health-plan premium denominator compresses margin, but as a *ceiling*, not a lower average (H2)
- Margin by `plan_materiality`: none (n=18) **5.46%**, minor (n=12) **2.27%**, material (n=10) **3.07%** — **non-monotonic**, so the simple "more plan → lower mean margin" claim is **not supported**. The `none` mean is inflated by the 4 for-profits (all `plan_materiality=none`); strip them and nonprofit-`none` falls to **2.96%**, statistically indistinct from minor/material at this n. (`h2_findings.md` §1–2)
- What **is** supported is a **ceiling / dispersion effect**: material plan owners have the **tightest spread (SD 2.16, range −0.2% to +7.4%)** of any group and **none exceeds 7.4%** (Baylor Scott & White is the ceiling), while plan-free systems reach 10.6% (BayCare). State it as **"material plan ownership coincides with a lower ceiling and less variance, not a lower center."** (`h2_findings.md` §2)
- **Kaiser Permanente #26 is the mechanical illustration:** **$711M operating income on $34,600M revenue = 2.1% margin** (`op_income_musd`,`op_revenue_musd`,`op_margin_pct`), with **88.7% `pct_other_days`** (highest in the list) because Worksheet S-3 routes its integrated-plan/Medicare-Advantage members into "other." A healthy dollar surplus divides down to a thin percentage because the denominator is mostly premium dollars. **Caveat:** `enriched_systems.csv` has **no premium-revenue / MLR column**, so "mostly premium" is the seed/spec characterization, **not quantified** here. (`h2_findings.md` §3; `pct_other_days` provenance: CMS Cost Report PUF FY2023, `SOURCES.md`)

### Factor 3 — Safety-net / payer exposure splits the academic medical centers (H4; also H3)
- The 11 AMCs (every row with "Academic medical center" in `archetype`) span **−4.5% to +9.6% (14.1 pp)** — nearly the whole list's spread. "AMCs are uniformly low" is **false**: an AMC (NYP +9.6%) is the strongest nonprofit on the board and an AMC (Montefiore −4.5%) is the weakest system overall. None carries a one-timer, so this spread is **structural, not an accounting artifact**. (`h4_findings.md` §1)
- The split runs on **DSH, and you must measure it with DSH, not Medicaid-day share:** margin vs `dsh_pct` is descriptively **Pearson −0.72**; margin vs `pct_medicaid_days` is **≈ 0 (+0.01)**. This is the measurement trap in `notes.md`: S-3 excludes managed-care/HMO Medicaid days from Title XIX, so in heavy managed-care states (NY, CA) Medicaid patients land in "other days." **Montefiore is the textbook case: only 7.4% Medicaid days but 29.2% DSH (highest of any AMC) and the worst margin.** (`h4_findings.md` §2; `dsh_pct`/`pct_medicaid_days` from CMS Cost Report PUF FY2023)
- **Destination AMCs (DSH < 8%, n=3: NYP, Mayo, Cleveland Clinic) average +6.83%; higher-DSH AMCs (DSH ≥ 8%, n=8) average +0.06%** — a **+6.77 pp** gap (Cohen's d ≈ +2.4). Carried at the top by NYP and Mayo, at the bottom by Montefiore and University Hospitals. (`h4_findings.md` §4)
- **Honesty flags:** it is **a DSH gradient with high outliers + a low tail, not a clean "bimodal" two-cluster split**; two systems break the gradient — **University Hospitals #39** (−3.3% margin but only mid 11.3% DSH) and **Mount Sinai NYC #30** (very high 26.6% DSH yet near break-even +0.7%). DSH is FY2023 **structural** data joined to a Q1-2026 margin; n=11. (`h4_findings.md` §3–4)
- **H3 (ambulatory/behavioral vs inpatient AMCs) is the same story in different clothes:** the ambulatory/behavioral + AdventHealth group out-earns the AMCs by ~9–13 pp raw (~9–10 pp normalized), but **the gap is tax status wearing a business-mix costume** — 4 of 5 in the group are for-profit, the lone nonprofit (AdventHealth +9.3%) actually **trails** NYP (+9.6%), and the AMCs that lose are the **safety-net** ones, not destination AMCs. **`case_mix_index` is empty for all 40 rows**, so "inpatient-heavy" cannot be measured directly — H3 is a hard-limited cut, reported as such. (`h3_findings.md` §1–3, §5)

### Factor 4 — One-time items & derived periods distort the top of the ranking (H6)
- **Tenet #1: $413M Conifer/CommonSpirit contract-conclusion gain → margin 24.1% → 16.4% (−7.7 pp).** Tenet **stays #1** (16.4% is still the highest), but its lead over #2 HCA collapses from **+12.1 pp to +4.4 pp** — the "runaway #1" is roughly **two-thirds a one-time accounting event.** (`h6_findings.md` §2; provenance verbatim in SEC THC 8-K ex-99.1 + 10-Q, `SOURCES.md`)
- **The only system that changes rank meaningfully is Community Health Systems #6 → #10** after stripping its **$90M** net impairment-and-gain-on-sale one-timer (9.5% → 6.4%). Everything else that "moves" (AdventHealth, Baylor S&W, Mayo, ProMedica each +1) is just sliding up past CHS. **35 of 40 systems do not move.** (`h6_findings.md` §3–4; CHS one-timer from SEC CYH 10-Q)
- **The advertised 28.6-pt spread shrinks to 20.9 pt** once the two sourced for-profit one-timers come out — all of the compression is at the top (Tenet); the floor is unchanged. (`h6_findings.md` §5)
- **Critical honesty requirement:** `one_time_items_musd` is populated for **only the 4 for-profits** (Tenet 413, CHS 90, HCA 0, UHS 0). **All 36 nonprofit cells are EMPTY / not_obtained** — no systematic nonprofit one-timer scan was completed. So the normalized ranking is a **partial normalization and a *lower bound* on the true distortion.** The article must **not** imply the normalized board is fully scrubbed. Per the prime directive, no nonprofit one-timer was invented to fill those cells. The **derived-period systems (Baylor Scott & White #8, Trinity #29) are flagged but contribute ZERO quantified movement** — there is no de-derived margin column; the calendar artifact is a caveat, not a measured shift. (`h6_findings.md` §1)

---

## 4. The "real signal inside the nonprofits" (article beat 4) — H5 (faith) + the AMC split

- **Catholic systems cluster at breakeven and the hypothesis holds cleanly for them:** Catholic (n=5) mean **+0.70%**, all five in the **bottom 17 of 40** (ranks 24,28,29,33,36), range −1.1% to +2.6%; **gap vs secular nonprofits (n=29, mean +3.05%) = −2.35 pp** (Cohen's d ≈ −0.71). Two are negative — **SSM Health −0.2%, Ascension −1.1%.** (`h5_findings.md` §1–2)
- **But "faith-based" as a monolith does NOT underperform:** the Adventist label (n=2) spans the **single best nonprofit operator on the board, AdventHealth +9.3%**, and a money-loser, **Adventist Health −1.8%** (distinct systems — name-trap honored). **"Catholic underperform" is defensible; "all faith-based underperform" is not.** (`h5_findings.md` §2)
- **Even the Catholic gap is entangled** with the H2 plan denominator (Providence and SSM own material plans; Trinity/Ascension minor), a derived period (Trinity #29), and parent-superset boundary flags (Ascension, Trinity). Read it as a **structural correlation, not a verdict on faith-based management.** The bottom of the whole table is **secular** safety-net AMCs (Montefiore, University Hospitals), not Catholic systems. (`h5_findings.md` §3)

---

## 5. The two non-levers: scale (H7) and digital maturity (H9)

### Scale does not predict margin (H7)
- Pearson margin vs **Q1 operating revenue = 0.107 (r² = 0.011)** — on the like-for-like basis, scale explains **~1%** of margin variance. Annual revenue **0.285**; beds **0.374** (still ~86% unexplained). (`h7_findings.md`)
- **The anchor pair holds exactly:** Kaiser (#26, **$34.6B** Q1 revenue, the largest) runs **2.1%**, while HCA (#2, ~half the Q1 revenue) runs **12.0%.** The faint positive tilt on annual revenue/beds is a **for-profit artifact** (HCA + Tenet are big *and* high-margin); **strip the 4 for-profits and every correlation collapses to ≈0** (r² ≈ 0.00 among the 36 nonprofits). Bigger is not more profitable here. (`h7_findings.md`)

### Digital / IT maturity does not independently predict margin (H9) — the dedicated finding
- **No usable correlation with any maturity signal.** Margin vs `cms_pi_metric` **Pearson −0.028** (n=40); margin vs `newsweek_smart_rank` **Pearson −0.101** (n=19; rank 1 = best, so a real positive relationship would show as negative r — this is too small to support even the direction). `chime_dhmw_level` and `himss_emram7_flag` are not continuous (only top-tier values are public), so they are used as indicators, not scales. (`h9_findings.md` §1)
- **The cleanest illustration — the CHIME DHMW Level-10 trio** (the only systems in the list at the published top digital tier; verified in `chime_dhmw_2025_level10_prnewswire.html`, name-traps cleared):

  | Rank | System | `op_margin_pct` | `cms_pi_metric` | `total_acute_beds` |
  |---:|---|---:|---:|---:|
  | 7 | AdventHealth | **+9.3%** | 0.9268 | 8,809 |
  | 24 | Bon Secours Mercy Health | **+2.6%** | 0.9459 | 5,641 |
  | 35 | Parkview Health | **−0.9%** | 0.9091 | 1,072 |

  The trio spans **−0.9% to +9.3% (10.2 pp ≈ 36% of the entire margin spread)**; trio mean **+3.67%** ≈ the all-40 mean (+3.91%). The most "digitally elite" cohort the data can identify sits **right at the field average, including a money-loser.** (`h9_findings.md` §3)
- **Independent cross-check:** the four systems with a Newsweek world-top-tier flagship (Mayo #1 +7.2%, Cleveland Clinic #2 +3.7%, Mass General Brigham #3 +0.3%, Mount Sinai #5 +0.7%) average **+2.98%** — at or below average margin. Same pattern, different signal. (`h9_findings.md` §3)
- **What the signals measure (so the null reads correctly):** `cms_pi_metric` is a **certified-EHR / interoperability participation/attestation** share for **CY2024** ("Meets criteria for promoting interoperability of EHRs," CMS dataset f4ga-b9gx) — **not an AI signal** and not a graded ladder. It is **bunched near a ceiling** (n=40, min 0.042, median 0.814, max 1.000; 34 of 40 ≥ 0.75), so it has little spread left to correlate with anything. The two systems that break low are explained by **footprint / operational events, not management quality**: UHS #3 (0.141 — only ~28 of 156 CCNs are PI-eligible; behavioral-heavy) and Ascension #36 (0.042 — a file-wide CY2024 "CEHRT Not Available" pattern, plausibly tied to the documented May-2024 ransomware incident; **flagged as a real-data outlier, not fixed**). Both UHS (+11.2%) and NYP (+9.6%, PI 0.375) are among the **highest** margins — the opposite of a maturity→margin link. (`h9_findings.md` §2, §5; `SOURCES.md` CMS-PI section)
- **Decoupling is the well-supported claim; "both downstream of capital" is interpretation.** In this file, **margin and maturity are independent (≈0)**, with maturity compressed near a ceiling — that is the measured result. The stronger "maturity and margin are both downstream of scale/capital" framing is the **design's interpretive argument** (DESIGN.md §6/§7), consistent with but **not proven by** the n=40 numbers (PI does not even track scale here: PI vs beds ≈ −0.12). Present the decoupling as measured; present "downstream of capital" as interpretation. The trio supports its spirit concretely: same top digital bar, beds 1,072 → 8,809, margins −0.9% → +9.3% — **digital tier shared, financial outcome not.** (`h9_findings.md` §4)
- **Selection-bias caveat (carry to article):** CHIME / Newsweek / HIMSS are **opt-in** recognition programs (non-applicants are invisible) and CMS-PI is participation, not capability depth — biased toward "looks digitally mature," which makes the *absence* of a margin relationship more notable, not less. **`unknown` ≠ "not digitally mature."** (`h9_findings.md` §2)

---

## 6. Geography is a weak covariate (H8)

- Among the **25 regionally-concentrated systems** (national operators excluded because HQ-state policy is not meaningful for a multi-state footprint), expansion-HQ (n=22) mean **+2.25%** vs non-expansion-HQ (n=3) **+7.00%** — the direction is the **opposite** of the naive "expansion helps margins" prior. (`h8_findings.md`)
- It is **noise**, not a driver: the non-expansion "group" is just **3 strong Southern commercial-growth systems — BayCare FL +10.6%, Baylor Scott & White TX +7.4%, Orlando Health FL +3.0%** (BayCare does most of the lifting). Ranges overlap almost completely (Y: −4.5% to +9.6%; N: +3.0% to +10.6%), and the worst margins in the cut (Montefiore, University Hospitals) are in **expansion** states. Expansion status is confounded with region/archetype. **Treat as a covariate, not a driver.** The `medicaid_expansion_hq` seed flag reconciles **0/40 mismatches** against `ref_kff_expansion.csv` (KFF, retrieved 2026-06-16). (`h8_findings.md`)

---

## 7. The chart pack (in `outputs/`, owned by P3-charts)

All six figures are present and back the beats above:
- **fig1_ranked_bar_by_ownership.png** — ranked margin bar colored by ownership (H1: for-profits clustered at top, the two nonprofit interlopers BayCare/NYP visible).
- **fig2_box_archetype_planmateriality.png** — box-plots by archetype and by `plan_materiality` (H2 ceiling/dispersion; H3/H4 AMC spread).
- **fig3_margin_vs_scale_beds.png** — margin-vs-scale scatter, bubble = beds (H7: flat; Kaiser/HCA anchor pair).
- **fig4_rerank_normalized.png** — before/after re-rank on normalized margin (H6: Tenet compresses, CHS drops #6→#10, spread 28.6→20.9).
- **fig5_regional_small_multiple.png** — regional small-multiple (H8: overlap, Southern non-expansion strength).
- **fig6_margin_vs_digital_maturity.png** — margin-vs-digital-maturity, bubble = revenue, Level-10 trio annotated (H9: no relationship; trio smeared across the range).

(Chart values are recomputed from the same `enriched_systems.csv` columns cited above; the **Parkview annual-revenue error in §8 affects any revenue-bubble sizing** — see flag.)

---

## 8. Open data-quality flags the article MUST respect (carried forward; none silently "fixed")

1. **Montefiore #40 floor (−$104.9M / −4.5%) is UNVERIFIED and possibly conflicting (Phase-0 flag F1, HIGH).** This is the article's headline floor ("…to −4.5%"). Reachable Becker's Q1-2026 Montefiore items are **smaller** (−$27.9M, ~−$88M; a separate $96.7M loss item) — **none equals −$104.9M / −4.5%.** Before publishing, either confirm the precise figure or **hedge the "−4.5%" endpoint**. The value is reported as-is from the seed and flagged; it was **not** reconstructed. Montefiore is one of 36 nonprofit rows, so the for-profit/nonprofit gap is unaffected, but the all-40 spread (28.6 pp) and the AMC floor depend on it. (`notes.md` Phase-0 §F1; `h1_findings.md` §6.5; `h4_findings.md`)
2. **Banner Health #19 revenue is out-of-tolerance (Phase-0 flag F2, MED).** Seed $4,100M rev / $180M income / stated 3.6% does not reconcile (180/4100 = 4.39%; income+margin imply revenue ≈ **$5,000M**). Per the reconciliation rule, revenue is the likely-wrong field. **Do not publish Banner's $4.1B revenue without confirmation.** Banner is mid-pack and does not drive any correlation; a correction would not change any directional finding. Reported as present, flagged, not corrected. (`notes.md` Phase-0 §F2; `h7_findings.md` caveat 3)
3. **Parkview Health #35 `annual_total_revenue_musd` = 549.4 is internally inconsistent** — it is *below* Parkview's single-quarter `op_revenue_musd` of 873.4, which is impossible for an annual figure. **Per the prime directive it was reported, not corrected.** Consequence: avoid any claim or **revenue-bubble chart** that depends on Parkview's annual revenue; the H7 annual-revenue correlation (0.285) is suspect on this row; the **trio's bed counts (1,072 / 5,641 / 8,809) are the reliable scale contrast**, not revenue. Recommend Matt verify against Parkview's audited financials. (`h7_findings.md` caveat 2; `h9_findings.md` §7.1)
4. **`case_mix_index` is EMPTY for all 40 rows** — no CMI field exists anywhere in the CMS Cost Report PUF (verified across 117 columns). Acuity cannot be used as an axis; H3/H4 say so explicitly. **Stated, never filled.** (`SOURCES.md` CMS Cost Report section; `h3_findings.md` §3; `h4_findings.md` §0)
5. **`cms_pi_metric` denominator ambiguity.** The column in `enriched_systems.csv` is the **all-CCN-denominator** variant (e.g., AdventHealth 0.9268). The P2-CMS-PI "primary" metric uses a **PI-listed-CCN** denominator and reports several of these systems at 1.000. **Both are real and sourced; they answer slightly different questions.** All H9 analysis used the **enriched-CSV column** consistently. The article should pick **one definition** and state it. (`h9_findings.md` §2, §7.2; `SOURCES.md` CMS-PI section)
6. **Boundary-match heterogeneity in scale columns.** Trinity #29 and Ascension #36 are `parent-superset` (AHRQ beds/revenue are **upper bounds** vs the Becker's Q1 entity); BJC #25 and Henry Ford #32 are `subset` (**lower bounds**); BayCare #4 has its AHRQ **scale columns intentionally EMPTY** (folded under the Trinity parent — attributing Trinity's national totals to BayCare's ~11 FL hospitals would be misattribution). Affects scale cuts only, and the parent-superset bias works *for* H7. (`enriched_systems.csv` `boundary_match`; `notes.md` mismatch log)
7. **Reporting-period heterogeneity.** Exactly 2 systems are `derived_3mo` — **Baylor Scott & White #8 (+7.4%)** and **Trinity #29 (+0.7%)** — both nonprofit; flagged, not excluded, not adjusted. (`enriched_systems.csv` `reporting_period`)
8. **HCRIS payer/DSH/UCC are FY2023 structural attributes**, not Q1-2026 figures (CMS lag). Present payer mix / DSH / uncompensated care as **stable structure**, never as 2026 financials. `uncompensated_care_musd` is a per-system **sum** and is a **lower bound** wherever `payer_status = partial` (18 of 40 systems). (`SOURCES.md` CMS Cost Report section)

---

## 9. What the article may and may not claim (guardrails)

**May claim (each backed above):** the ranking is a structure map; tax status is the single largest sorter at the extremes; the plan denominator caps plan-owners' margins (Kaiser as illustration); AMCs are bimodal-ish on DSH (measure with DSH, not Medicaid days); one-timers inflate the top (Tenet ~two-thirds of its lead is one-time; CHS the only real rank mover; spread 28.6→20.9); Catholic systems cluster at breakeven but "faith-based" as a whole does not; scale and digital maturity do **not** sort the board; geography is a weak covariate.

**May NOT claim:** that for-profits are better operators (the gap conflates structure); that owning a plan lowers the *average* margin (only the ceiling); that any maturity signal predicts margin; that the normalized board is fully scrubbed (only 4 of 40 one-timers sourced); that "maturity is downstream of capital" is *measured* (it is interpretation); any **p-value, significance test, or causal mechanism**; the **Becker's umbrella headline as a verified citation**; the precise **Montefiore −4.5%** and **Banner $4.1B** figures without the §8 hedges; or any number depending on **Parkview's annual revenue** or **`case_mix_index`** (does not exist).

**Citation guidance (per `notes.md` F3 + CLAUDE.md zero-tolerance):** cite the **underlying primary/secondary sources per system** — SEC filings for the 4 for-profits (THC, HCA, UHS, CYH 10-Qs/XBRL; all in `SOURCES.md`), Becker's per-system items + system newsrooms for the rest, and CMS/AHRQ/KFF/NCSL/CHIME/Newsweek/HIMSS for the structural layers — **not** the unverifiable umbrella headline.
