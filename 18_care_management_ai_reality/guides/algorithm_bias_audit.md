# Algorithm Bias Audit Checklist

## Why This Matters

Obermeyer et al.'s landmark 2019 *Science* study found that a widely used commercial algorithm systematically under-identified Black patients for care management. At the same risk score, Black patients were considerably sicker.

**The mechanism**: The algorithm predicted *costs*, not *health*. Because of systemic access barriers, Black patients utilize fewer resources at the same level of illness.

**The fix**: Adjusting the algorithm would increase Black patients eligible for care management from 17.7% to 46.5%.

This checklist helps you audit your own algorithms for similar biases.

---

## Pre-Audit Preparation

### Required Data
- [ ] Algorithm specifications/documentation
- [ ] Training data characteristics
- [ ] Prediction target variable definition
- [ ] Current stratification thresholds
- [ ] Demographic data for scored population
- [ ] Clinical outcomes data (independent of the algorithm)

### Required Expertise
- [ ] Data scientist or statistician
- [ ] Clinical subject matter expert
- [ ] Health equity/disparities expert
- [ ] Representative from affected community (advisory)

---

## Audit Checklist

### Section 1: Label Bias Assessment

**What does the algorithm predict?**

| Question | Answer | Risk Level |
|----------|--------|------------|
| Is the prediction target a *cost* variable? | Yes/No | If Yes: HIGH |
| Is the target based on *utilization* patterns? | Yes/No | If Yes: HIGH |
| Does the target assume equal access to care? | Yes/No | If Yes: HIGH |
| Is the target a clinical outcome (e.g., mortality, HbA1c, readmission)? | Yes/No | If No: MEDIUM |

**High-risk labels** (likely to encode bias):
- Total cost of care
- Number of ED visits
- Inpatient admissions
- "Utilization" composite scores

**Lower-risk labels** (but still require validation):
- Mortality (but check for differential documentation)
- Lab values (HbA1c, LDL)
- Functional status assessments

### Section 2: Outcome Parity Testing

For each demographic group, compare:

```
Algorithm Risk Score at Percentile X → Actual Clinical Burden

Example:
Members at 90th percentile risk score:
- Group A: Average chronic conditions = 4.2
- Group B: Average chronic conditions = 5.8

If Group B is sicker at the same score, the algorithm under-identifies Group B.
```

**Test the following dimensions:**
- [ ] Race/ethnicity
- [ ] Primary language
- [ ] Insurance type (Medicaid vs. commercial)
- [ ] Geographic area (urban vs. rural)
- [ ] Disability status
- [ ] Age groups

**Sample SQL for Parity Testing:**
```sql
WITH risk_deciles AS (
    SELECT
        member_id,
        risk_score,
        NTILE(10) OVER (ORDER BY risk_score) AS risk_decile,
        race_ethnicity,
        chronic_condition_count,
        hospitalization_count_12m,
        avg_hba1c
    FROM risk_stratification rs
    JOIN member_demographics md ON rs.member_id = md.member_id
    JOIN clinical_indicators ci ON rs.member_id = ci.member_id
)
SELECT
    risk_decile,
    race_ethnicity,
    COUNT(*) AS members,
    AVG(chronic_condition_count) AS avg_chronic_conditions,
    AVG(hospitalization_count_12m) AS avg_hospitalizations,
    AVG(avg_hba1c) AS avg_hba1c
FROM risk_deciles
GROUP BY risk_decile, race_ethnicity
ORDER BY risk_decile DESC, race_ethnicity;
```

**Interpretation**: At each decile, clinical burden should be similar across groups. Significant differences indicate bias.

### Section 3: Access Barrier Proxy Variables

Check if the algorithm uses variables that may proxy for access barriers:

| Variable | Potential Bias | Mitigation |
|----------|----------------|------------|
| Prior healthcare costs | Penalizes those with access barriers | Exclude or weight down |
| Number of PCP visits | Penalizes those without PCP access | Use as denominator, not numerator |
| Pharmacy fills | Penalizes those with cost/access issues | Adjust for neighborhood pharmacy access |
| Preventive screenings | Penalizes those with work schedule constraints | Weight by opportunity, not completion |
| "Engagement" scores | Penalizes those unreachable during business hours | Exclude from risk score |

### Section 4: Training Data Representativeness

**Questions to answer:**

1. What time period was the training data from?
   - Pre-ACA data may not reflect current population
   - COVID-period data may have distortions

2. Which populations were excluded from training?
   - New members (no history)
   - Members with incomplete data
   - Decedents (may be most relevant)

3. Are training data demographics representative of the current population?
   - Compare training data demographics to current enrollment
   - Identify under-represented groups

### Section 5: Disparate Impact Testing

Calculate intervention rates by group:

```
Intervention Rate = (Members in group flagged for intervention) / (Members in group)

Disparate Impact Ratio = Intervention Rate (Minority Group) / Intervention Rate (Reference Group)

If ratio < 0.8, there may be disparate impact (EEOC guideline adapted).
```

**Example:**
```
Group A (reference): 12% flagged for care management
Group B: 8% flagged for care management
Ratio: 8/12 = 0.67 → Potential disparate impact
```

---

## Remediation Options

### Option 1: Re-train with Clinical Outcomes

Replace cost-based labels with clinical outcomes:
- Mortality risk
- Hospital readmission (actual events, not cost)
- Disease progression (HbA1c trends, functional decline)

### Option 2: Calibration Adjustment

Apply group-specific thresholds to achieve clinical parity:

```python
# Simplified example
def adjusted_threshold(risk_score, demographic_group):
    calibration_factors = {
        'Group_A': 1.0,
        'Group_B': 0.85,  # Lower threshold to increase identification
        'Group_C': 0.90
    }
    return risk_score >= (base_threshold * calibration_factors.get(demographic_group, 1.0))
```

### Option 3: Exclude Biased Variables

Remove or down-weight variables that encode access rather than health:
- Prior costs
- Utilization counts (without access adjustment)
- "Engagement" or "compliance" flags

### Option 4: Add Clinical Override

Allow clinicians to override algorithmic exclusion when clinical judgment indicates need.

---

## Documentation Requirements

After completing the audit, document:

1. **Audit date and participants**
2. **Algorithm version audited**
3. **Findings by section**
4. **Parity test results (attach data)**
5. **Identified biases and their magnitude**
6. **Remediation plan with timeline**
7. **Monitoring plan for ongoing bias detection**

---

## Ongoing Monitoring

After remediation, establish:

- **Quarterly parity reports** by demographic group
- **Alert thresholds** for disparate impact ratios < 0.8
- **Annual full audit** with community advisory input

---

## References

Obermeyer Z, Powers B, Vogeli C, Mullainathan S. (2019). Dissecting Racial Bias in an Algorithm Used to Manage the Health of Populations. *Science*, 366(6464), 447-453.

Rajkomar A, Hardt M, Howell MD, Corrado G, Chin MH. (2018). Ensuring Fairness in Machine Learning to Advance Health Equity. *Annals of Internal Medicine*, 169(12), 866-872.

---

*Part of the Vitals & Variables Edition 18 Toolkit: Care Management AI vs. Member Reality*
