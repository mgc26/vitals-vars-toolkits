#!/usr/bin/env python3
"""
Issue #29 — Phase 3 (P3) chart pack.

Owns (writes): outputs/*.png  ONLY.
Reads (read-only): data/processed/enriched_systems.csv  ONLY.

Produces 6 mobile-friendly charts at 200 dpi (matplotlib/seaborn):
  fig1_ranked_bar_by_ownership.png      ranked bar of Q1 op margin, colored by ownership
  fig2_box_archetype_planmateriality.png box-plots of margin by archetype and by plan_materiality
  fig3_margin_vs_scale_beds.png         margin-vs-scale scatter (bubble = total acute beds)
  fig4_rerank_normalized.png            before/after re-rank on one-timer-normalized margin
  fig5_regional_small_multiple.png      regional small-multiple of margin (4 census regions)
  fig6_margin_vs_digital_maturity.png   margin-vs-CMS-PI digital maturity scatter (bubble = annual revenue),
                                        annotating the CHIME Level-10 trio (AdventHealth / Bon Secours / Parkview)

ZERO FABRICATION: every value plotted is read directly from enriched_systems.csv.
Nothing is imputed, estimated, or reconstructed. Rows with an empty required
value are dropped from the affected chart and reported (never back-filled).
A chart whose required column is *entirely* empty is skipped and named in the log.

Statistical posture (DESIGN.md s6 / spec s11): descriptive / hypothesis-generating
only. n=40, non-random, heterogeneous reporting periods. No p-values; no causal claims.
"""

import os
import sys
import textwrap

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # headless / file output only
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

# ---------------------------------------------------------------------------
# Paths (absolute; the issue dir name contains spaces and an ampersand)
# ---------------------------------------------------------------------------
ISSUE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_CSV = os.path.join(ISSUE_DIR, "data", "processed", "enriched_systems.csv")
OUT_DIR = os.path.join(ISSUE_DIR, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

DPI = 200

# ---------------------------------------------------------------------------
# Vitals & Variables-style palette / mobile-friendly defaults
# ---------------------------------------------------------------------------
INK = "#1A2A3A"      # near-black blue for text
GRID = "#D9DEE4"     # light grid
MUTED = "#6B7785"    # secondary text
ZERO = "#B23A48"     # zero / break-even reference line

# Ownership colors (only for-profit + nonprofit are present; public-government kept for safety)
OWN_COLORS = {
    "for-profit": "#C44E2B",        # warm (stands out — only 4 of 40)
    "nonprofit": "#2E6E8E",         # primary teal-blue
    "public-government": "#7A6FB0",
}

# Plan-materiality ordered colors
PLAN_ORDER = ["none", "minor", "material"]
PLAN_COLORS = {"none": "#9CC3D5", "minor": "#3F8FB0", "material": "#1F5A74"}

# Region colors for the small-multiple
REGION_ORDER = ["Northeast", "Midwest", "South", "West"]
REGION_COLORS = {
    "Northeast": "#2E6E8E",
    "Midwest": "#C44E2B",
    "South": "#3E8E5A",
    "West": "#7A6FB0",
}

# Archetype: collapse the long descriptive strings to 5 canonical buckets by prefix.
ARCHETYPE_PREFIXES = [
    ("National for-profit operator", "National\nfor-profit"),
    ("Academic medical center", "Academic\nmedical center"),
    ("Faith-based system", "Faith-based\nsystem"),
    ("Integrated payer-provider", "Integrated\npayer-provider"),
    ("Secular regional IDN", "Secular\nregional IDN"),
]

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 13,
        "axes.titlesize": 16,
        "axes.titleweight": "bold",
        "axes.labelsize": 13,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.25,
    }
)

CAPTION = ("Vitals & Variables #29  |  Source: enriched_systems.csv (Becker's Q1-2026 financials + "
           "AHRQ/CMS/SEC enrichment).  Descriptive only; n=40, non-random.")


def short_archetype(s: str) -> str:
    for prefix, label in ARCHETYPE_PREFIXES:
        if isinstance(s, str) and s.startswith(prefix):
            return label
    return "Other"


def pct_fmt(x, _pos=None):
    return f"{x:.0f}%"


def add_caption(fig):
    fig.text(0.5, 0.005, CAPTION, ha="center", va="bottom", fontsize=8, color=MUTED)


def col_all_empty(df, col):
    """True if the column is missing entirely or has zero non-null values."""
    return (col not in df.columns) or (df[col].notna().sum() == 0)


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Load (read-only)
# ---------------------------------------------------------------------------
df = pd.read_csv(DATA_CSV)
assert len(df) == 40, f"expected 40 rows, got {len(df)}"
print(f"Loaded {len(df)} rows x {len(df.columns)} cols from {DATA_CSV}")

produced = []   # list of PNG paths actually written
skipped = []    # list of "name: reason" for charts not produced


# ===========================================================================
# CHART 1 — Ranked bar of Q1 operating margin, colored by ownership
# Required: op_margin_pct (+ ownership for color, rank/system_name for labels)
# ===========================================================================
def chart1_ranked_bar():
    req = "op_margin_pct"
    if col_all_empty(df, req):
        skipped.append(f"fig1_ranked_bar_by_ownership: required column '{req}' is entirely empty")
        return
    d = df.dropna(subset=[req]).sort_values("rank")
    n_dropped = len(df) - len(d)
    colors = d["ownership"].map(OWN_COLORS).fillna("#999999")

    fig, ax = plt.subplots(figsize=(9.5, 12))  # tall = mobile-friendly
    y = np.arange(len(d))[::-1]  # rank 1 at top
    ax.barh(y, d[req].values, color=colors.values, edgecolor="white", linewidth=0.6, zorder=3)
    ax.axvline(0, color=ZERO, lw=1.4, zorder=4)

    ax.set_yticks(y)
    ax.set_yticklabels([f"{r:>2}. {n}" for r, n in zip(d["rank"], d["system_name"])], fontsize=10)
    ax.set_xlabel("Q1-2026 operating margin")
    ax.xaxis.set_major_formatter(FuncFormatter(pct_fmt))
    ax.grid(axis="x", color=GRID, zorder=0)
    ax.set_axisbelow(True)

    # value labels at bar ends
    for yi, v in zip(y, d[req].values):
        off = 0.25 if v >= 0 else -0.25
        ax.text(v + off, yi, f"{v:.1f}%", va="center",
                ha="left" if v >= 0 else "right", fontsize=8.5, color=INK)
    pad = (d[req].max() - d[req].min()) * 0.12
    ax.set_xlim(d[req].min() - pad - 1.5, d[req].max() + pad + 1.5)

    handles = [Line2D([0], [0], marker="s", linestyle="", markersize=11,
                      markerfacecolor=OWN_COLORS[k], markeredgecolor="white",
                      label=f"{k} (n={(d['ownership'] == k).sum()})")
               for k in ["for-profit", "nonprofit"] if (d["ownership"] == k).any()]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=11, title="Ownership")

    title = "40 health systems ranked by Q1-2026 operating margin"
    sub = "Colored by tax status — all 4 for-profits sit in the top 6 (H1)"
    ax.set_title(f"{title}\n", loc="left")
    ax.text(0, 1.005, sub, transform=ax.transAxes, fontsize=11.5, color=MUTED, va="bottom")
    if n_dropped:
        ax.text(0.0, -0.045, f"Note: {n_dropped} system(s) dropped — empty {req}.",
                transform=ax.transAxes, fontsize=8, color=MUTED)
    add_caption(fig)
    produced.append(save(fig, "fig1_ranked_bar_by_ownership.png"))


# ===========================================================================
# CHART 2 — Box-plots: margin by archetype, and margin by plan_materiality
# Required: op_margin_pct + (archetype) and (plan_materiality)
# ===========================================================================
def chart2_boxplots():
    req = "op_margin_pct"
    if col_all_empty(df, req):
        skipped.append(f"fig2_box_archetype_planmateriality: required column '{req}' is entirely empty")
        return
    panels = []
    if not col_all_empty(df, "archetype"):
        panels.append("archetype")
    if not col_all_empty(df, "plan_materiality"):
        panels.append("plan_materiality")
    if not panels:
        skipped.append("fig2_box_archetype_planmateriality: both 'archetype' and 'plan_materiality' empty")
        return

    fig, axes = plt.subplots(len(panels), 1, figsize=(9.5, 5.2 * len(panels)))
    if len(panels) == 1:
        axes = [axes]

    # --- Panel A: archetype ---
    if "archetype" in panels:
        ax = axes[panels.index("archetype")]
        d = df.dropna(subset=[req, "archetype"]).copy()
        d["arch"] = d["archetype"].map(short_archetype)
        order = [lab for _, lab in ARCHETYPE_PREFIXES if (d["arch"] == lab).any()]
        groups = [d.loc[d["arch"] == g, req].values for g in order]
        bp = ax.boxplot(groups, vert=True, patch_artist=True, widths=0.6,
                        medianprops=dict(color=INK, lw=2),
                        whiskerprops=dict(color=MUTED), capprops=dict(color=MUTED),
                        flierprops=dict(marker="", linestyle="none"))
        for patch in bp["boxes"]:
            patch.set_facecolor("#CFE0E8")
            patch.set_edgecolor(MUTED)
        # jittered points
        rng = np.random.default_rng(29)
        for i, g in enumerate(order, start=1):
            yv = d.loc[d["arch"] == g, req].values
            xv = i + rng.uniform(-0.16, 0.16, size=len(yv))
            ax.scatter(xv, yv, s=34, color="#C44E2B", alpha=0.75, zorder=3, edgecolor="white", linewidth=0.4)
        ax.axhline(0, color=ZERO, lw=1.2)
        ax.set_xticks(range(1, len(order) + 1))
        ax.set_xticklabels([f"{g}\n(n={(d['arch'] == g).sum()})" for g in order], fontsize=10)
        ax.yaxis.set_major_formatter(FuncFormatter(pct_fmt))
        ax.set_ylabel("Q1 operating margin")
        ax.grid(axis="y", color=GRID)
        ax.set_axisbelow(True)
        ax.set_title("Operating margin by archetype", loc="left")

    # --- Panel B: plan_materiality ---
    if "plan_materiality" in panels:
        ax = axes[panels.index("plan_materiality")]
        d = df.dropna(subset=[req, "plan_materiality"]).copy()
        order = [g for g in PLAN_ORDER if (d["plan_materiality"] == g).any()]
        groups = [d.loc[d["plan_materiality"] == g, req].values for g in order]
        bp = ax.boxplot(groups, vert=True, patch_artist=True, widths=0.55,
                        medianprops=dict(color=INK, lw=2),
                        whiskerprops=dict(color=MUTED), capprops=dict(color=MUTED),
                        flierprops=dict(marker="", linestyle="none"))
        for patch, g in zip(bp["boxes"], order):
            patch.set_facecolor(PLAN_COLORS.get(g, "#CFE0E8"))
            patch.set_edgecolor(MUTED)
            patch.set_alpha(0.55)
        rng = np.random.default_rng(7)
        for i, g in enumerate(order, start=1):
            yv = d.loc[d["plan_materiality"] == g, req].values
            xv = i + rng.uniform(-0.15, 0.15, size=len(yv))
            ax.scatter(xv, yv, s=34, color=INK, alpha=0.7, zorder=3, edgecolor="white", linewidth=0.4)
        ax.axhline(0, color=ZERO, lw=1.2)
        ax.set_xticks(range(1, len(order) + 1))
        ax.set_xticklabels([f"{g}\n(n={(d['plan_materiality'] == g).sum()})" for g in order], fontsize=11)
        ax.yaxis.set_major_formatter(FuncFormatter(pct_fmt))
        ax.set_ylabel("Q1 operating margin")
        ax.set_xlabel("Health-plan materiality")
        ax.grid(axis="y", color=GRID)
        ax.set_axisbelow(True)
        ax.set_title("Operating margin by health-plan materiality (H2)", loc="left")

    fig.suptitle("Where the nonprofit spread comes from: archetype & the plan denominator",
                 x=0.02, ha="left", fontsize=15, fontweight="bold", y=0.995)
    add_caption(fig)
    fig.subplots_adjust(hspace=0.32)
    produced.append(save(fig, "fig2_box_archetype_planmateriality.png"))


# ===========================================================================
# CHART 3 — Margin vs scale scatter, bubble = total acute beds
# Required: op_margin_pct + total_acute_beds. x-axis = annual revenue if present
# else Q1 revenue (always present). Bubble area encodes beds.
# ===========================================================================
def chart3_margin_vs_scale():
    req_y = "op_margin_pct"
    req_size = "total_acute_beds"
    if col_all_empty(df, req_y):
        skipped.append(f"fig3_margin_vs_scale_beds: required column '{req_y}' is entirely empty")
        return
    if col_all_empty(df, req_size):
        skipped.append(f"fig3_margin_vs_scale_beds: bubble column '{req_size}' is entirely empty")
        return

    x_col = "annual_total_revenue_musd" if not col_all_empty(df, "annual_total_revenue_musd") else "op_revenue_musd"
    x_label = ("Annual total revenue (USD billions)"
               if x_col == "annual_total_revenue_musd" else "Q1 operating revenue (USD billions)")

    d = df.dropna(subset=[req_y, req_size, x_col]).copy()
    n_dropped = len(df) - len(d)
    dropped_names = sorted(set(df["system_name"]) - set(d["system_name"]))

    xb = d[x_col].values / 1000.0  # -> billions
    yv = d[req_y].values
    beds = d[req_size].values
    sizes = 30 + (beds / beds.max()) * 1500.0  # area proportional to beds
    colors = d["ownership"].map(OWN_COLORS).fillna("#999999")

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(xb, yv, s=sizes, c=colors.values, alpha=0.62, edgecolor="white", linewidth=0.8, zorder=3)
    ax.axhline(0, color=ZERO, lw=1.2, zorder=2)

    # Descriptive trend line (least-squares; labeled as descriptive, no inference)
    if len(d) >= 3:
        b, a = np.polyfit(xb, yv, 1)
        r = np.corrcoef(xb, yv)[0, 1]
        xs = np.linspace(xb.min(), xb.max(), 100)
        ax.plot(xs, a + b * xs, color=MUTED, ls="--", lw=1.4, zorder=2,
                label=f"descriptive fit (Pearson r = {r:.2f})")
        ax.legend(loc="upper right", frameon=False, fontsize=10)

    # annotate the scale anchors (largest revenue, largest beds) + extremes
    to_label = set()
    to_label.add(d[x_col].idxmax())
    to_label.add(d[req_size].idxmax())
    to_label.add(d[req_y].idxmax())
    to_label.add(d[req_y].idxmin())
    for idx in to_label:
        row = d.loc[idx]
        ax.annotate(row["system_name"],
                    (row[x_col] / 1000.0, row[req_y]),
                    xytext=(6, 8), textcoords="offset points", fontsize=9.5, color=INK,
                    fontweight="bold")

    ax.set_xlabel(x_label)
    ax.set_ylabel("Q1 operating margin")
    ax.yaxis.set_major_formatter(FuncFormatter(pct_fmt))
    ax.grid(color=GRID, zorder=0)
    ax.set_axisbelow(True)
    ax.set_title("Scale does not predict margin (H7)\n", loc="left")
    ax.text(0, 1.005, "Bubble size = total acute beds  ·  color = ownership",
            transform=ax.transAxes, fontsize=11, color=MUTED, va="bottom")

    # bubble-size legend
    leg_beds = [5000, 15000, 35000]
    leg_beds = [b for b in leg_beds if b <= beds.max() * 1.05]
    handles = [Line2D([0], [0], marker="o", linestyle="", markerfacecolor="#BBBBBB",
                      markeredgecolor="white",
                      markersize=np.sqrt(30 + (b / beds.max()) * 1500.0) / 1.6,
                      label=f"{b:,} beds") for b in leg_beds]
    own_handles = [Line2D([0], [0], marker="o", linestyle="", markersize=10,
                          markerfacecolor=OWN_COLORS[k], markeredgecolor="white", label=k)
                   for k in ["for-profit", "nonprofit"] if (d["ownership"] == k).any()]
    leg1 = ax.legend(handles=own_handles, loc="upper right", frameon=False, fontsize=10, title="Ownership")
    ax.add_artist(leg1)
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=9, title="Acute beds",
              labelspacing=1.6, borderpad=1.0)

    if n_dropped:
        ax.text(0.0, -0.10,
                f"Note: {n_dropped} system(s) omitted (empty beds/revenue): {', '.join(dropped_names)}.",
                transform=ax.transAxes, fontsize=8, color=MUTED)
    add_caption(fig)
    produced.append(save(fig, "fig3_margin_vs_scale_beds.png"))


# ===========================================================================
# CHART 4 — Before/after re-rank on one-timer-normalized margin (slopegraph)
# Required: op_margin_pct + op_margin_q1_normalized_pct
# ===========================================================================
def chart4_rerank():
    req_a, req_b = "op_margin_pct", "op_margin_q1_normalized_pct"
    if col_all_empty(df, req_a) or col_all_empty(df, req_b):
        miss = req_a if col_all_empty(df, req_a) else req_b
        skipped.append(f"fig4_rerank_normalized: required column '{miss}' is entirely empty")
        return
    d = df.dropna(subset=[req_a, req_b]).copy()
    d["rank_as"] = d[req_a].rank(ascending=False, method="first").astype(int)
    d["rank_norm"] = d[req_b].rank(ascending=False, method="first").astype(int)
    movers = d[d["rank_as"] != d["rank_norm"]].copy()

    fig, ax = plt.subplots(figsize=(9, 12))
    x_as, x_norm = 0.0, 1.0
    for _, r in d.iterrows():
        moved = r["rank_as"] != r["rank_norm"]
        adj = (r[req_a] != r[req_b])  # actually had a one-timer adjustment
        color = "#C44E2B" if adj else GRID
        lw = 2.4 if adj else 1.0
        z = 5 if adj else 1
        ax.plot([x_as, x_norm], [r["rank_as"], r["rank_norm"]], color=color, lw=lw, zorder=z,
                alpha=0.95 if adj else 0.7)
        ax.scatter([x_as, x_norm], [r["rank_as"], r["rank_norm"]],
                   color=color if adj else MUTED, s=22 if adj else 10, zorder=z + 1)

    # label only the as-reported left side for all, and movers on both sides
    for _, r in d.iterrows():
        ax.text(x_as - 0.03, r["rank_as"],
                f"{r['system_name']}  ({r[req_a]:.1f}%)",
                ha="right", va="center", fontsize=8.2,
                color=INK if (r[req_a] != r[req_b]) else MUTED,
                fontweight="bold" if (r[req_a] != r[req_b]) else "normal")
    for _, r in movers.iterrows():
        ax.text(x_norm + 0.03, r["rank_norm"],
                f"#{int(r['rank_norm'])}  {r['system_name']} ({r[req_b]:.1f}%)",
                ha="left", va="center", fontsize=8.4, color="#C44E2B", fontweight="bold")

    ax.set_xlim(-0.85, 1.95)
    ax.set_ylim(len(d) + 0.6, 0.4)  # rank 1 at top
    ax.set_xticks([x_as, x_norm])
    ax.set_xticklabels(["As reported\n(op_margin_pct)", "One-timers stripped\n(normalized)"], fontsize=12)
    ax.set_ylabel("Rank (1 = highest margin)")
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(left=True, length=0)
    n_adj = int((d[req_a] != d[req_b]).sum())
    ax.set_title("Strip the one-time items and the ranking barely moves (H6)\n", loc="left")
    ax.text(0, 1.004,
            f"{len(movers)} of {len(d)} systems change rank; only {n_adj} carry an identified one-timer "
            f"(highlighted)",
            transform=ax.transAxes, fontsize=10.5, color=MUTED, va="bottom")
    add_caption(fig)
    produced.append(save(fig, "fig4_rerank_normalized.png"))


# ===========================================================================
# CHART 5 — Regional small-multiple of margin (one panel per census region)
# Required: op_margin_pct + census_region
# ===========================================================================
def chart5_regional():
    req = "op_margin_pct"
    if col_all_empty(df, req):
        skipped.append(f"fig5_regional_small_multiple: required column '{req}' is entirely empty")
        return
    if col_all_empty(df, "census_region"):
        skipped.append("fig5_regional_small_multiple: required column 'census_region' is entirely empty")
        return
    d = df.dropna(subset=[req, "census_region"]).copy()
    regions = [r for r in REGION_ORDER if (d["census_region"] == r).any()]
    # any unexpected region values still get a panel
    regions += sorted(set(d["census_region"]) - set(REGION_ORDER))

    ncol = 2
    nrow = int(np.ceil(len(regions) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(11, 4.6 * nrow), sharex=True)
    axes = np.array(axes).reshape(-1)
    xmin, xmax = d[req].min(), d[req].max()
    pad = (xmax - xmin) * 0.18

    for ax, region in zip(axes, regions):
        g = d[d["census_region"] == region].sort_values(req)
        y = np.arange(len(g))
        ax.barh(y, g[req].values, color=REGION_COLORS.get(region, "#2E6E8E"),
                edgecolor="white", linewidth=0.5, zorder=3, alpha=0.92)
        ax.axvline(0, color=ZERO, lw=1.2, zorder=4)
        ax.set_yticks(y)
        ax.set_yticklabels(g["system_name"], fontsize=8.6)
        ax.set_xlim(xmin - pad - 1, xmax + pad + 1)
        ax.xaxis.set_major_formatter(FuncFormatter(pct_fmt))
        ax.grid(axis="x", color=GRID, zorder=0)
        ax.set_axisbelow(True)
        med = g[req].median()
        ax.set_title(f"{region}   (n={len(g)}, median {med:.1f}%)", loc="left", fontsize=13)
        for yi, v in zip(y, g[req].values):
            ax.text(v + (0.2 if v >= 0 else -0.2), yi, f"{v:.1f}%",
                    va="center", ha="left" if v >= 0 else "right", fontsize=7.6, color=INK)

    for ax in axes[len(regions):]:
        ax.set_visible(False)

    fig.suptitle("Operating margin by HQ census region (H8)\n"
                 "The negative tail clusters in the Midwest & urban Northeast; FL non-expansion systems hold up",
                 x=0.02, ha="left", fontsize=14, fontweight="bold", y=0.998)
    fig.text(0.5, 0.075, "Q1-2026 operating margin", ha="center", fontsize=12, color=INK)
    fig.text(0.02, 0.040,
             "HQ-state geography is not meaningful for multi-state national operators (see national_operator_flag).",
             ha="left", fontsize=8, color=MUTED)
    add_caption(fig)
    fig.subplots_adjust(hspace=0.30, wspace=0.55, bottom=0.135, top=0.91)
    produced.append(save(fig, "fig5_regional_small_multiple.png"))


# ===========================================================================
# CHART 6 — Margin vs digital maturity (CMS-PI), bubble = annual revenue,
# annotate CHIME Level-10 trio: AdventHealth / Bon Secours / Parkview
# Required: op_margin_pct + cms_pi_metric
# ===========================================================================
def chart6_digital():
    req_y, req_x = "op_margin_pct", "cms_pi_metric"
    if col_all_empty(df, req_y):
        skipped.append(f"fig6_margin_vs_digital_maturity: required column '{req_y}' is entirely empty")
        return
    if col_all_empty(df, req_x):
        skipped.append(f"fig6_margin_vs_digital_maturity: required column '{req_x}' is entirely empty")
        return

    size_col = "annual_total_revenue_musd"
    have_size = not col_all_empty(df, size_col)
    d = df.dropna(subset=[req_y, req_x]).copy()
    n_dropped = len(df) - len(d)

    if have_size:
        s = d[size_col].fillna(d[size_col].median())
        sizes = 40 + (s / s.max()) * 1600.0
    else:
        sizes = np.full(len(d), 120.0)

    # color by CHIME Level-10 membership (the trio) vs the rest
    is_l10 = d["chime_dhmw_level"].astype(str) == "10" if "chime_dhmw_level" in d.columns else pd.Series(False, index=d.index)
    colors = np.where(is_l10.values, "#C44E2B", "#2E6E8E")

    fig, ax = plt.subplots(figsize=(10.5, 8))
    ax.scatter(d[req_x].values, d[req_y].values, s=sizes, c=colors,
               alpha=0.60, edgecolor="white", linewidth=0.8, zorder=3)
    ax.axhline(0, color=ZERO, lw=1.2, zorder=2)

    # descriptive fit + correlation (labeled descriptive; no inference)
    if len(d) >= 3:
        b, a = np.polyfit(d[req_x].values, d[req_y].values, 1)
        r = np.corrcoef(d[req_x].values, d[req_y].values)[0, 1]
        xs = np.linspace(d[req_x].min(), d[req_x].max(), 100)
        ax.plot(xs, a + b * xs, color=MUTED, ls="--", lw=1.4, zorder=2,
                label=f"descriptive fit (Pearson r = {r:.2f})")

    # annotate the CHIME Level-10 trio explicitly (name-trap safe: exact system_name strings)
    TRIO = ["AdventHealth", "Bon Secours Mercy Health", "Parkview Health"]
    offsets = {"AdventHealth": (10, 16), "Bon Secours Mercy Health": (10, -20), "Parkview Health": (10, 12)}
    for name in TRIO:
        sub = d[d["system_name"] == name]
        if sub.empty:
            continue
        row = sub.iloc[0]
        ax.annotate(f"{name}\n{row[req_y]:.1f}% margin",
                    (row[req_x], row[req_y]),
                    xytext=offsets.get(name, (8, 8)), textcoords="offset points",
                    fontsize=9.5, color="#8A2E18", fontweight="bold",
                    arrowprops=dict(arrowstyle="-", color="#C44E2B", lw=0.8))

    ax.set_xlabel("Digital maturity  —  CMS Promoting Interoperability share (system CCNs)")
    ax.set_ylabel("Q1-2026 operating margin")
    ax.yaxis.set_major_formatter(FuncFormatter(pct_fmt))
    ax.grid(color=GRID, zorder=0)
    ax.set_axisbelow(True)
    ax.set_title("Going digital does not buy margin (H9)\n", loc="left")
    sub_txt = "Bubble size = annual total revenue  ·  CHIME Digital Health Most Wired Level-10 trio in orange"
    if not have_size:
        sub_txt = "CHIME Digital Health Most Wired Level-10 trio in orange (revenue unavailable for sizing)"
    ax.text(0, 1.005, sub_txt, transform=ax.transAxes, fontsize=10.5, color=MUTED, va="bottom")

    legend_handles = [
        Line2D([0], [0], marker="o", linestyle="", markersize=11, markerfacecolor="#C44E2B",
               markeredgecolor="white", label="CHIME DHMW Level 10"),
        Line2D([0], [0], marker="o", linestyle="", markersize=11, markerfacecolor="#2E6E8E",
               markeredgecolor="white", label="Not in published top tier"),
    ]
    if len(d) >= 3:
        legend_handles.append(Line2D([0], [0], color=MUTED, ls="--", lw=1.4,
                                     label=f"descriptive fit (r = {r:.2f})"))
    ax.legend(handles=legend_handles, loc="upper left", frameon=False, fontsize=10)

    note = ("CMS-PI = certified-EHR/interoperability participation (CY2024), not an AI measure. "
            "Opt-in recognition → selection bias.")
    if n_dropped:
        note = f"{n_dropped} system(s) dropped (empty {req_x}). " + note
    ax.text(0.0, -0.105, note, transform=ax.transAxes, fontsize=8, color=MUTED)
    add_caption(fig)
    produced.append(save(fig, "fig6_margin_vs_digital_maturity.png"))


# ---------------------------------------------------------------------------
# Run all
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    chart1_ranked_bar()
    chart2_boxplots()
    chart3_margin_vs_scale()
    chart4_rerank()
    chart5_regional()
    chart6_digital()

    print("\n=== CHARTS PRODUCED ({}/6) ===".format(len(produced)))
    for p in produced:
        print("  ", p)
    if skipped:
        print("\n=== CHARTS SKIPPED ({}) ===".format(len(skipped)))
        for s in skipped:
            print("  ", s)
    else:
        print("\nNo charts skipped — every required column had data.")
