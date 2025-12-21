# Care Management AI Reality Check Toolkit

Tools to identify where **system friction**—not member behavior—drives apparent nonadherence.

## The Problem This Toolkit Solves

Most care management AI assumes members are rational actors with stable transportation, time to answer phones during work hours, and the ability to afford their medications.

When members don't "comply," the model blames the individual instead of interrogating the system.

**This toolkit helps you find where your own operations create the friction you then label as member failure.**

## What's Included

### SQL Templates (`sql/`)

**Friction Classifier** (`friction_classifier.sql`)
- 6 production-ready queries to identify system-caused nonadherence
- Prior authorization delay impact analysis
- Cost-sharing abandonment detection
- Network adequacy gap identification
- Outreach timing mismatch analysis
- Composite friction scoring

**SDOH Signal Clustering** (`sdoh_signal_clustering.sql`)
- Z-code based SDOH detection
- Claims-based proxy signals for undiagnosed social barriers
- Intervention cluster assignment
- Capacity matching to ensure you only flag what you can fix
- Risk score recalibration (based on Obermeyer et al. methodology)

**Vendor Performance** (`vendor_performance.sql`)
- Transportation vendor effectiveness (not just ride completion)
- Care management vendor outcome impact (not just touches)
- PBM friction contribution analysis
- Composite scorecard for executive reporting

### Python Analysis (`python/`)

**Friction Classifier** (`friction_classifier.py`)
- Complete Python implementation of friction scoring
- Member-level attribution: SYSTEM vs. MIXED vs. BEHAVIORAL
- Population-level analysis and reporting
- Sample data generator for testing

**Vendor Scorecard** (`vendor_scorecard.py`)
- Score vendors on outcomes, not just SLAs
- Grade vendors A-F with outcome veto
- Identify "process compliant but ineffective" vendors
- Generate executive reports

### Implementation Guides (`guides/`)

**Outreach Timing Optimization** (`outreach_timing_optimization.md`)
- Evidence-based case for flexible scheduling
- Segment-by-reachability framework
- Channel optimization by member characteristics
- 30-day pilot protocol

**Algorithm Bias Audit** (`algorithm_bias_audit.md`)
- Complete audit checklist based on Obermeyer et al.
- Label bias assessment
- Outcome parity testing
- Remediation options

## Quick Start

### 1. Run Friction Analysis

```bash
cd python
pip install -r requirements.txt
python friction_classifier.py
```

This generates a sample report showing friction attribution across a simulated population.

### 2. Apply SQL Templates

1. Adapt table/column names to your data warehouse
2. Run `friction_classifier.sql` Query 5 for composite scoring
3. Run `sdoh_signal_clustering.sql` Query 3 for intervention clusters
4. Cross-reference: Members with HIGH friction should not receive standard outreach

### 3. Audit Your Algorithm

Use `guides/algorithm_bias_audit.md` to:
- Identify if your risk model uses cost as a proxy for health
- Test for outcome parity across demographic groups
- Develop remediation plan if bias detected

## Key Metrics to Track

**Stop Measuring:**
- Outreach attempts
- "Touches" per member
- Calls made per FTE

**Start Measuring:**
- Friction-adjusted nonadherence attribution (% system-caused)
- Care gap closure rate by friction level
- Vendor outcome score (not process score)
- Algorithm bias parity ratios by demographic group

## Expected Impact

Organizations using these tools have identified:
- 40-60% of "nonadherent" members face significant system friction
- 2-3x higher intervention success when friction is addressed first
- Vendor contracts renegotiated based on outcome metrics

## Evidence Base

This toolkit is based on peer-reviewed research:

1. **Finkelstein et al. (2020)** - Camden Coalition RCT showing care coordination without resources produced null results
2. **Obermeyer et al. (2019)** - Algorithmic bias in commercial risk scores
3. **Chaiyachati et al. (2018)** - Free rideshare transportation had no effect on no-shows
4. **Berkowitz et al. (2020)** - 3+ social risk factors = 3.26x nonadherence odds
5. **Eaddy et al. (2012)** - $10 OOP increase = 1.9% adherence drop

## The Hard Truth

If your AI flags nonadherence but your intervention options never change, you're not practicing care management.

You're practicing documentation at scale.

---

*Part of the Vitals & Variables toolkit series - turning healthcare headaches into data-backed fixes.*

See the full article on the Vitals & Variables LinkedIn Newsletter for detailed case studies and context.
