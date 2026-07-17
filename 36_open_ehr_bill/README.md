# The Bill and the Risk: Cost Model (Issue 36)

Part 3 of the Open EHR Experiment. The 5-year TCO + gated plausibility model for a self-hosted
open-source EHR (the Part 2 stack) across four buyer segments. Interactive calculator:
https://vv-issue36-bill.vercel.app

The Part 2 assembled slice this model prices is live as a synthetic-data demo (a narrow vertical slice, NOT a
complete EHR; same 34.5% build, read-mostly, not for clinical use): https://vv-issue35-ehr.vercel.app

## The verdict (computed, pre-committed gates)
Implausible for all four segments today. The economics gate (the computed, falsifiable swing
factor) fails everywhere; the three hospital segments also fail the declared safety and
liability gates. Greenfield cash-pay is the least-implausible, but it still fails TWO gates,
not one: safety (the structural MFA and backup gaps apply to any clinic, not just a hospital,
and were unproven in Part 2) and economics. Its economics is the one honest close call in the
set: it loses at the midpoint but would win at the favorable end of the ranges, whereas the
three hospitals lose even with every assumption stacked in the build's favor (see
robustness_certificate.md).

## 5-year TCO midpoints (build vs best alternative)
- Regional IDN: build $115.1M vs stay-put $16.6M
- Community hospital: build $37.0M vs stay-put $3.0M
- Large system: build $316.6M vs stay-put $39.8M
- Greenfield cash-pay: build $7.4M vs unbundle $5.0M

## Files
- cost_model.csv: every cost cell with tier (sourced/derived/estimate), low/high, unit.
- robustness_certificate.md: economics verdict re-decided at each segment's build-favorable
  cost extreme (does an in-range estimate choice flip it?).

## Tiers + honesty
- sourced: a public benchmark, cited. derived: computed from sourced primitives (recomputed
  by the validator, not hand-typed). estimate: a stated-assumption range, not a point.
- Most lines are estimate-tier because the refs give defensible RANGES, not single quotes;
  that is the honest label and the disclosed judgment surface. The calculator exposes the
  drivers as sliders so you re-run with your own numbers.
- This is a MODEL, not a quote: a 5-year range, not a promise.
- The reasoned gates (safety, liability) are pre-committed editorial dispositions, committed to
  the public git log BEFORE any cost cell was committed. Economics is the computed gate. One
  disposition (greenfield safety) was corrected pass to fail after an adversarial review, in the
  open, to comply with its own pre-committed rule; the git history shows the change.
