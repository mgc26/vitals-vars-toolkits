# The Bill and the Risk: Cost Model (Issue 36)

Part 3 of the Open EHR Experiment. The 5-year TCO + gated plausibility model for a self-hosted
open-source EHR (the Part 2 stack) across four buyer segments. Interactive calculator:
https://vv-issue36-bill.vercel.app

## The verdict (computed, pre-committed gates)
Implausible for all four segments today. The economics gate (the computed, falsifiable swing
factor) fails everywhere; the three hospital segments also fail the declared safety and
liability gates. Greenfield cash-pay is the least-implausible: it clears safety, liability,
migration, and governance, and fails on economics ALONE (a cash-pay clinic buys SaaS for less).

## 5-year TCO midpoints (build vs best alternative)
- Regional IDN: build $115.1M vs stay-put $16.6M
- Community hospital: build $37.0M vs stay-put $3.0M
- Large system: build $316.6M vs stay-put $39.8M
- Greenfield cash-pay: build $7.4M vs unbundle $5.0M

## Files
- : every cost cell with tier (sourced/derived/estimate), low/high, unit.

## Tiers + honesty
- sourced: a public benchmark, cited. derived: computed from sourced primitives (recomputed
  by the validator, not hand-typed). estimate: a stated-assumption range, not a point.
- Most lines are estimate-tier because the refs give defensible RANGES, not single quotes;
  that is the honest label and the disclosed judgment surface. The calculator exposes the
  drivers as sliders so you re-run with your own numbers.
- This is a MODEL, not a quote: a 5-year range, not a promise.
- The reasoned gates (safety, liability) are pre-committed editorial dispositions, fixed in
  the public git log BEFORE any cost number was authored. Economics is the computed gate.
