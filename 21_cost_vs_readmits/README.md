# Hospital Cost vs. Readmissions Analysis Toolkit

Reproducible analysis comparing state-level hospital spending with Medicare readmission rates.

## Quick Start

1. **Run the Analysis** → Execute the Python script
2. **View Results** → Scatter plot + hexbin density visualization
3. **Interpret** → Correlation statistics and quadrant breakdown

## What's Included

### Python Analysis (`python/`)
- `vitals_vars_21_generate.py` - Complete analysis script
- Embedded data from KFF and Commonwealth Fund
- Generates publication-ready charts (200 dpi)
- Computes Pearson and Spearman correlations

## Key Findings

- **Sample**: n=48 states with complete data
- **Pearson r**: -0.20 (p=0.18) - not significant
- **Spearman rho**: -0.12 (p=0.42) - not significant
- **Interpretation**: Hospital spending per inpatient day does not predict Medicare readmission rates at the state level

## Data Sources

1. **Hospital Expenses**: KFF State Health Facts (2024), nonprofit community hospitals, expense per adjusted inpatient day. Source: AHA Annual Survey.

2. **Readmissions**: Commonwealth Fund Medicare State Scorecard (Oct 2025), Appendix D. 30-day hospital readmissions among FFS Medicare beneficiaries per 1,000 (2023 CMS CCW data).

## Getting Started

```bash
cd python
pip install pandas numpy matplotlib scipy
python vitals_vars_21_generate.py
```

## Output Files

The script generates:
- `vitals_vars_21_cost_vs_readmits_scatter.png` - Labeled scatter plot with outliers
- `vitals_vars_21_cost_vs_readmits_hexbin.png` - Density plot showing state clustering

## Caveats

- Correlation is not causation
- State-level aggregation masks hospital-level variation
- Different populations: all nonprofit hospitals (expenses) vs. Medicare FFS only (readmissions)

## Questions?

See the full analysis on Vitals & Variables LinkedIn Newsletter for clinical context and implementation guidance.

---

*Part of the Vitals & Variables toolkit series - turning healthcare questions into data-backed answers.*
