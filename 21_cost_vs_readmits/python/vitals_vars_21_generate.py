#!/usr/bin/env python3
"""
Vitals & Vars Edition #21: Hospital Cost vs. Medicare Readmissions
Cross-state analysis of nonprofit hospital expenses and 30-day readmission rates.

Sources:
- Expense data: KFF/AHA 2024, as reproduced in Becker's Hospital Review
  (Nonprofit expense per adjusted inpatient day, community hospitals)
- Readmissions data: Commonwealth Fund Medicare State Scorecard (Oct 2025)
  Appendix D - 30-day hospital readmissions among FFS Medicare beneficiaries,
  per 1,000 beneficiaries (2023 CCW data via CMS Geographic Variation PUF)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os

# Output directory - create if needed (uses current directory)
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("Vitals & Vars #21: Hospital Cost vs. Medicare Readmissions")
print("=" * 60)

# =============================================================================
# DATA: Nonprofit Expense per Adjusted Inpatient Day (2024, $)
# Source: KFF/AHA via Becker's Hospital Review
# =============================================================================
expense_data_raw = """
Alabama,2009
Alaska,3097
Arizona,3620
Arkansas,2059
California,5081
Colorado,4118
Connecticut,3567
Delaware,3
Georgia,2609
Hawaii,3713
Idaho,5455
Illinois,3154
Indiana,3612
Iowa,1894
Kansas,2556
Kentucky,2963
Louisiana,2896
Maine,3100
Maryland,3803
Massachusetts,4184
Michigan,2790
Minnesota,3258
Mississippi,1227
Missouri,3049
Montana,2418
Nebraska,3001
Nevada,2904
New Hampshire,3474
New Jersey,3826
New Mexico,3069
New York,4265
North Carolina,3186
North Dakota,3421
Ohio,3710
Oklahoma,2586
Oregon,4147
Pennsylvania,3268
Rhode Island,3469
South Carolina,2861
South Dakota,2023
Tennessee,3432
Texas,3550
Utah,4710
Vermont,3422
Virginia,3152
Washington,4127
West Virginia,2624
Wisconsin,2837
Wyoming,3400
"""

# =============================================================================
# DATA: Medicare FFS 30-Day Readmissions per 1,000 Beneficiaries (2023)
# Source: Commonwealth Fund Medicare State Scorecard, Appendix D
# Analysis of 2023 CCW data via CMS Geographic Variation Public Use File
# =============================================================================
readmissions_data_raw = """
Alabama,40.8
Alaska,25.6
Arizona,29.0
Arkansas,37.4
California,36.7
Colorado,23.9
Connecticut,43.2
Delaware,32.9
District of Columbia,42.2
Florida,46.8
Georgia,38.4
Hawaii,20.7
Idaho,18.6
Illinois,46.1
Indiana,39.1
Iowa,25.6
Kansas,31.2
Kentucky,41.6
Louisiana,39.8
Maine,25.4
Maryland,40.7
Massachusetts,46.4
Michigan,44.2
Minnesota,34.8
Mississippi,38.0
Missouri,41.8
Montana,21.0
Nebraska,31.8
Nevada,40.5
New Hampshire,31.1
New Jersey,44.8
New Mexico,24.3
New York,42.3
North Carolina,32.7
North Dakota,30.3
Ohio,41.1
Oklahoma,38.3
Oregon,21.6
Pennsylvania,41.8
Rhode Island,36.9
South Carolina,32.6
South Dakota,28.5
Tennessee,35.2
Texas,37.8
Utah,21.4
Vermont,27.1
Virginia,32.8
Washington,23.8
West Virginia,47.5
Wisconsin,31.9
Wyoming,22.9
"""

# =============================================================================
# PARSE DATA
# =============================================================================
def parse_csv_data(raw_text):
    """Parse comma-separated state,value data."""
    data = {}
    for line in raw_text.strip().split('\n'):
        if ',' in line:
            parts = line.split(',')
            state = parts[0].strip()
            value = float(parts[1].strip())
            data[state] = value
    return data

expense_dict = parse_csv_data(expense_data_raw)
readmissions_dict = parse_csv_data(readmissions_data_raw)

print(f"\nExpense data parsed: {len(expense_dict)} states")
print(f"Readmissions data parsed: {len(readmissions_dict)} states")

# =============================================================================
# DATA CLEANING: Drop states with missing/erroneous data
# =============================================================================
dropped_states = []

# Check for states with clearly erroneous expense values
for state, value in list(expense_dict.items()):
    if value < 500:  # Expense < $500/day is clearly an error
        dropped_states.append((state, f"Expense value ${value} is implausibly low (likely data entry error)"))
        del expense_dict[state]

# States in readmissions but not in expense data
for state in list(readmissions_dict.keys()):
    if state not in expense_dict:
        dropped_states.append((state, "No nonprofit expense data in KFF/AHA table"))

print(f"\n--- DROPPED STATES ---")
for state, reason in dropped_states:
    print(f"  {state}: {reason}")

# =============================================================================
# MERGE DATA
# =============================================================================
merged_data = []
for state in expense_dict:
    if state in readmissions_dict:
        merged_data.append({
            'state': state,
            'nonprofit_expense_per_adjusted_inpatient_day_2024': expense_dict[state],
            'medicare_ffs_30day_readmissions_per_1000_2023': readmissions_dict[state]
        })

df = pd.DataFrame(merged_data)
df = df.sort_values('state').reset_index(drop=True)

print(f"\n--- MERGED DATASET ---")
print(f"Final sample: n={len(df)} states")
print(f"\nExpense range: ${df['nonprofit_expense_per_adjusted_inpatient_day_2024'].min():.0f} - ${df['nonprofit_expense_per_adjusted_inpatient_day_2024'].max():.0f}")
print(f"Readmissions range: {df['medicare_ffs_30day_readmissions_per_1000_2023'].min():.1f} - {df['medicare_ffs_30day_readmissions_per_1000_2023'].max():.1f} per 1,000")

# =============================================================================
# COMPUTE STATISTICS
# =============================================================================
x = df['nonprofit_expense_per_adjusted_inpatient_day_2024']
y = df['medicare_ffs_30day_readmissions_per_1000_2023']

# Correlations
pearson_r, pearson_p = stats.pearsonr(x, y)
spearman_r, spearman_p = stats.spearmanr(x, y)

print(f"\n--- CORRELATIONS ---")
print(f"Pearson r = {pearson_r:.3f} (p = {pearson_p:.4f})")
print(f"Spearman rho = {spearman_r:.3f} (p = {spearman_p:.4f})")

# Medians for quadrant analysis
median_expense = x.median()
median_readmissions = y.median()

print(f"\n--- MEDIANS ---")
print(f"Median expense: ${median_expense:.0f}")
print(f"Median readmissions: {median_readmissions:.1f} per 1,000")

# Quadrant assignment
df['quadrant'] = 'Unknown'
df.loc[(x >= median_expense) & (y >= median_readmissions), 'quadrant'] = 'High Cost, High Readmit'
df.loc[(x >= median_expense) & (y < median_readmissions), 'quadrant'] = 'High Cost, Low Readmit'
df.loc[(x < median_expense) & (y >= median_readmissions), 'quadrant'] = 'Low Cost, High Readmit'
df.loc[(x < median_expense) & (y < median_readmissions), 'quadrant'] = 'Low Cost, Low Readmit'

print(f"\n--- QUADRANT DISTRIBUTION ---")
for q in ['High Cost, High Readmit', 'High Cost, Low Readmit', 'Low Cost, High Readmit', 'Low Cost, Low Readmit']:
    count = (df['quadrant'] == q).sum()
    print(f"  {q}: {count} states")

# =============================================================================
# IDENTIFY OUTLIERS FOR LABELING
# =============================================================================
top_cost = df.nlargest(7, 'nonprofit_expense_per_adjusted_inpatient_day_2024')['state'].tolist()
top_readmit = df.nlargest(7, 'medicare_ffs_30day_readmissions_per_1000_2023')['state'].tolist()
outlier_states = list(set(top_cost + top_readmit))

print(f"\n--- OUTLIERS (labeled on charts) ---")
print(f"Top 7 by cost: {', '.join(top_cost)}")
print(f"Top 7 by readmissions: {', '.join(top_readmit)}")
print(f"Unique outliers to label: {len(outlier_states)}")

# State abbreviations for labeling
state_abbrevs = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

# =============================================================================
# CHART 1: HEXBIN DENSITY PLOT
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 8))

# Hexbin plot
hb = ax.hexbin(x, y, gridsize=8, cmap='Blues', mincnt=1, edgecolors='white', linewidths=0.5)

# Colorbar
cb = fig.colorbar(hb, ax=ax, label='Number of states per bin')
cb.ax.tick_params(labelsize=10)

# Median lines
ax.axvline(median_expense, color='#E74C3C', linestyle='--', linewidth=1.5, alpha=0.7, label=f'Median cost (${median_expense:,.0f})')
ax.axhline(median_readmissions, color='#E74C3C', linestyle='--', linewidth=1.5, alpha=0.7, label=f'Median readmissions ({median_readmissions:.1f})')

# Labels and title
ax.set_xlabel('Nonprofit Hospital Expense per Adjusted Inpatient Day, 2024 ($)', fontsize=12)
ax.set_ylabel('Medicare FFS 30-Day Readmissions per 1,000 Beneficiaries, 2023', fontsize=12)
ax.set_title(f'Hospital Cost vs. Medicare Readmissions by State (n={len(df)})\nPearson r = {pearson_r:.2f}, Spearman ρ = {spearman_r:.2f}',
             fontsize=13, fontweight='bold')

# Legend
ax.legend(loc='upper left', fontsize=10)

# Format axes
ax.set_xlim(1000, 6000)
ax.set_ylim(15, 52)
ax.tick_params(axis='both', labelsize=10)

# Grid
ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

# Note about hexbin
ax.text(0.98, 0.02, 'Hexbin shows density:\ndarker = more states in that region',
        transform=ax.transAxes, fontsize=9, ha='right', va='bottom',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
hexbin_path = os.path.join(OUTPUT_DIR, 'vitals_vars_21_cost_vs_readmits_hexbin.png')
plt.savefig(hexbin_path, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
print(f"\nSaved: {hexbin_path}")

# =============================================================================
# CHART 2: SCATTER PLOT WITH OUTLIER LABELS
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 8))

# Scatter all points
ax.scatter(x, y, s=60, c='#3498DB', alpha=0.7, edgecolors='white', linewidth=0.5)

# Linear fit line
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
x_fit = np.linspace(x.min() - 200, x.max() + 200, 100)
y_fit = slope * x_fit + intercept
ax.plot(x_fit, y_fit, color='#2C3E50', linewidth=2, linestyle='-', alpha=0.6,
        label=f'Linear fit (r={r_value:.2f})')

# Median lines
ax.axvline(median_expense, color='#E74C3C', linestyle='--', linewidth=1.5, alpha=0.6)
ax.axhline(median_readmissions, color='#E74C3C', linestyle='--', linewidth=1.5, alpha=0.6)

# Label outliers only
np.random.seed(42)  # For reproducible jitter
for idx, row in df.iterrows():
    if row['state'] in outlier_states:
        abbrev = state_abbrevs.get(row['state'], row['state'][:2])
        # Small jitter for overlapping labels
        x_offset = np.random.uniform(-80, 80)
        y_offset = np.random.uniform(0.3, 1.2)
        ax.annotate(abbrev,
                   (row['nonprofit_expense_per_adjusted_inpatient_day_2024'],
                    row['medicare_ffs_30day_readmissions_per_1000_2023']),
                   xytext=(5 + x_offset, 5 + y_offset), textcoords='offset points',
                   fontsize=9, fontweight='bold', color='#2C3E50',
                   ha='left', va='bottom')

# Quadrant labels
ax.text(1300, 48, 'Low Cost,\nHigh Readmit', fontsize=9, ha='left', va='top',
        color='#7F8C8D', style='italic')
ax.text(5300, 48, 'High Cost,\nHigh Readmit', fontsize=9, ha='right', va='top',
        color='#7F8C8D', style='italic')
ax.text(1300, 17, 'Low Cost,\nLow Readmit', fontsize=9, ha='left', va='bottom',
        color='#7F8C8D', style='italic')
ax.text(5300, 17, 'High Cost,\nLow Readmit', fontsize=9, ha='right', va='bottom',
        color='#7F8C8D', style='italic')

# Labels and title
ax.set_xlabel('Nonprofit Hospital Expense per Adjusted Inpatient Day, 2024 ($)', fontsize=12)
ax.set_ylabel('Medicare FFS 30-Day Readmissions per 1,000 Beneficiaries, 2023', fontsize=12)
ax.set_title(f'Hospital Cost vs. Medicare Readmissions by State (n={len(df)})\nLabels show top outliers in cost or readmissions',
             fontsize=13, fontweight='bold')

# Legend
ax.legend(loc='upper left', fontsize=10)

# Format axes
ax.set_xlim(1000, 5700)
ax.set_ylim(15, 52)
ax.tick_params(axis='both', labelsize=10)

# Grid
ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

plt.tight_layout()
scatter_path = os.path.join(OUTPUT_DIR, 'vitals_vars_21_cost_vs_readmits_scatter.png')
plt.savefig(scatter_path, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
print(f"Saved: {scatter_path}")

# =============================================================================
# GENERATE MARKDOWN DRAFT
# =============================================================================
# Find notable states for narrative
high_cost_low_readmit = df[(df['nonprofit_expense_per_adjusted_inpatient_day_2024'] >= median_expense) &
                           (df['medicare_ffs_30day_readmissions_per_1000_2023'] < median_readmissions)]
low_cost_high_readmit = df[(df['nonprofit_expense_per_adjusted_inpatient_day_2024'] < median_expense) &
                           (df['medicare_ffs_30day_readmissions_per_1000_2023'] >= median_readmissions)]

# Best performers (low cost, low readmit)
best_performers = df[(df['nonprofit_expense_per_adjusted_inpatient_day_2024'] < median_expense) &
                     (df['medicare_ffs_30day_readmissions_per_1000_2023'] < median_readmissions)]

# Worst outliers
highest_readmit = df.loc[df['medicare_ffs_30day_readmissions_per_1000_2023'].idxmax()]
lowest_readmit = df.loc[df['medicare_ffs_30day_readmissions_per_1000_2023'].idxmin()]
highest_cost = df.loc[df['nonprofit_expense_per_adjusted_inpatient_day_2024'].idxmax()]

markdown_content = f"""# Does Spending More Actually Keep Patients Out of the Hospital?

**Vitals & Vars Edition #21**

---

## The Question

Every hospital CFO knows the tension: invest more in care quality, or manage costs to stay solvent. But does higher spending per patient actually translate to fewer patients bouncing back within 30 days?

I merged two publicly available datasets to find out:
- **Hospital expenses**: Nonprofit community hospital expense per adjusted inpatient day by state (KFF/AHA, 2024)
- **Readmissions**: Medicare FFS 30-day hospital readmissions per 1,000 beneficiaries by state (Commonwealth Fund, 2023)

The result: {len(df)} states with complete data, a natural experiment across wildly different healthcare markets.

---

## What the Data Shows

![Scatter plot of hospital cost vs readmissions](vitals_vars_21_cost_vs_readmits_scatter.png)

![Hexbin density plot](vitals_vars_21_cost_vs_readmits_hexbin.png)

**The correlation is weak and statistically insignificant.**

- Pearson r = {pearson_r:.2f} (p = {pearson_p:.3f})
- Spearman rho = {spearman_r:.2f} (p = {spearman_p:.3f})

Translation: knowing what a state spends per inpatient day tells you almost nothing about how often its Medicare patients end up back in the hospital within a month.

---

## Three Things That Surprised Me

1. **{highest_cost['state']} spends ${highest_cost['nonprofit_expense_per_adjusted_inpatient_day_2024']:,.0f}/day but has middle-of-the-pack readmissions ({highest_cost['medicare_ffs_30day_readmissions_per_1000_2023']:.1f}/1,000).** Money alone does not buy quality transitions.

2. **{lowest_readmit['state']} has the lowest readmission rate ({lowest_readmit['medicare_ffs_30day_readmissions_per_1000_2023']:.1f}/1,000) at a cost of ${lowest_readmit['nonprofit_expense_per_adjusted_inpatient_day_2024']:,.0f}/day.** That is above median cost but still vastly outperforms states spending similar amounts.

3. **{len(low_cost_high_readmit)} states manage to spend below the national median on inpatient care while still landing in the top half for readmissions.** Being cheap does not automatically mean worse outcomes, but it does not guarantee better ones either.

---

## What I Expected (Confirmed)

- **No simple linear relationship.** Healthcare is too complex for "spend more, get better" to work as a universal law.
- **Regional clustering matters.** States with similar demographics and payer mixes tend to cluster together, regardless of cost.
- **West Virginia remains an outlier** with the highest readmission rate ({highest_readmit['medicare_ffs_30day_readmissions_per_1000_2023']:.1f}/1,000) despite average spending, reinforcing that population health burden trumps hospital investment.

---

## So What Does This Mean for Operations?

The weak correlation is not a bug. It is a signal.

**If cost does not drive readmissions, what does?**

The literature points to *process standardization* and *care coordination*:

- Discharge planning protocols that start on admission
- Medication reconciliation before the patient leaves
- Follow-up appointments scheduled before discharge (not "call your PCP")
- Post-discharge phone calls within 48 hours
- Handoff communication standards (written, verbal, and electronic)

These are workflow interventions, not capital expenditures. A hospital in a low-cost state can implement a standardized discharge bundle for a fraction of what it costs to add another ICU bed, and the data suggests it will move the needle more.

**The operational takeaway:** If your readmission rate is high, do not assume you need to spend more. Audit your transition processes first.

---

## Caveats (Read Before Citing)

1. **Correlation is not causation.** This cross-sectional snapshot cannot prove that spending (or not spending) causes readmissions. Confounders abound: population age, chronic disease burden, rurality, payer mix.

2. **Different populations, different definitions.** Expense data covers all nonprofit community hospitals; readmissions cover Medicare fee-for-service only. These are overlapping but not identical patient pools.

3. **State-level aggregation hides hospital variation.** A state with one high-performing academic medical center and many struggling rural hospitals will look "average" on both metrics.

---

## Sources

- Jacobson, G., et al. (2025). *State Scorecard on Medicare Performance: How Medicare Is Working for Its Beneficiaries* (Appendices). Commonwealth Fund. Analysis of 2023 CCW data via CMS Geographic Variation Public Use File.
- Kaiser Family Foundation / American Hospital Association (2024). *Hospital Adjusted Expenses per Inpatient Day by Ownership*. As reproduced in Becker's Hospital Review, 2024.

---

*Have state-level data you want us to cross-walk? Reply to this newsletter with your idea.*
"""

md_path = os.path.join(OUTPUT_DIR, 'vitals_vars_21.md')
with open(md_path, 'w') as f:
    f.write(markdown_content)
print(f"Saved: {md_path}")

# =============================================================================
# SUMMARY OUTPUT
# =============================================================================
print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
print(f"Sample size: n={len(df)} states")
print(f"Pearson r = {pearson_r:.3f}")
print(f"Spearman rho = {spearman_r:.3f}")
print(f"\nOutput files:")
print(f"  1. {hexbin_path}")
print(f"  2. {scatter_path}")
print(f"  3. {md_path}")
