# EHR Optimization Quick Wins

Low-effort, high-impact interventions to reduce clinical slop immediately.

These are proven optimizations from peer-reviewed literature and industry case studies. Each can be implemented in days to weeks, not months.

---

## Quick Win #1: Redundant Field Audit & Removal

**Time to Implement:** 2-4 weeks
**Typical Impact:** 15-25% documentation time reduction
**Evidence:** Duke Health removed 433 redundant fields, achieved 18.5% time reduction

### The Problem
EHRs accumulate fields over time. Fields added for one use case remain forever, even when no longer needed. Clinicians click through dozens of irrelevant fields to complete documentation.

### How to Identify
Run this analysis on your EHR:
```sql
-- Find fields with <5% completion rate (likely unnecessary)
SELECT
    form_name,
    field_name,
    COUNT(*) AS total_encounters,
    SUM(CASE WHEN field_value IS NOT NULL THEN 1 ELSE 0 END) AS completed_count,
    ROUND((SUM(CASE WHEN field_value IS NOT NULL THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)) * 100, 1) AS completion_pct
FROM ehr_form_fields
WHERE encounter_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY form_name, field_name
HAVING (SUM(CASE WHEN field_value IS NOT NULL THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)) < 0.05
ORDER BY total_encounters DESC;
```

### Implementation Steps
1. **Audit flowsheets, reassessment forms, and discharge templates**
   - Pull 90-day completion rates for all fields
   - Flag fields with <5% completion (likely unused)
   - Review with clinical stakeholders

2. **Categorize fields**
   - **Remove:** <5% completion, no regulatory requirement
   - **Make optional:** 5-20% completion, not safety-critical
   - **Keep required:** >20% completion or regulatory mandate

3. **Build test environment**
   - Remove/hide flagged fields in test instance
   - Pilot with 10-15 clinicians for 1 week
   - Measure: Time per assessment (before vs. after)

4. **Deploy to production**
   - Staged rollout by department
   - Monitor for issues (missing required data)
   - Rapid rollback capability if needed

### Expected Outcomes
- **15-25% reduction** in documentation time per encounter
- **50-90% fewer clicks** for common workflows
- Improved clinician satisfaction scores

### Cost
- **Implementation:** 24-40 hours of informatics time
- **Value:** For 100 nurses at $90/hr saving 10 min/shift: **$468K/year**

---

## Quick Win #2: Medication Reconciliation Streamlining

**Time to Implement:** 3-6 weeks
**Typical Impact:** 30-50% reduction in duplicate med entries
**Evidence:** Industry benchmarks show med rec done 3-5x per admission

### The Problem
The same medication list gets entered in:
- ED triage
- ED physician assessment
- Admission H&P
- Pharmacy verification
- Nursing MAR

Each step creates opportunities for discrepancies, rework, and errors.

### Single-Source-of-Truth Design
**Goal:** Medication list entered ONCE, referenced everywhere.

1. **Designate canonical source**
   - Usually: Pharmacy system or admission med rec
   - All other locations REFERENCE, don't re-enter

2. **Auto-populate downstream**
   - ED med list → auto-populates admission
   - Admission list → auto-populates MAR
   - Pharmacy changes → propagate to all views

3. **Flag discrepancies, don't duplicate**
   - If clinician sees different med than canonical list
   - Present: "Canonical list shows X, you're entering Y. Update canonical list?"
   - Don't allow parallel, conflicting lists

### Implementation Steps
1. **Map current state**
   - Diagram: Where is med rec currently done?
   - Count: Average duplicate entries per admission
   - Time: How long does each entry take?

2. **Configure auto-population**
   - Most EHRs support this (Epic SmartLists, Cerner PowerPlans)
   - Build rules: If med list exists in System A, pull to System B

3. **Disable duplicate entry points**
   - Remove ability to create separate med lists
   - Force: "Use existing list or update canonical source"

4. **Pilot in ED → Inpatient workflow**
   - 1 ED, 1 inpatient unit
   - Measure: Duplicate entry instances before vs. after
   - Measure: Discrepancy rate (safety metric)

### Expected Outcomes
- **30-50% reduction** in duplicate med entries
- **2-5 minutes saved** per med rec (at $90/hr: $3-$7.50 each)
- **Reduced discrepancy-related safety events**

### Cost
- **Implementation:** 40-60 hours (workflows + build + training)
- **Value:** For 10,000 admissions/year saving 5 min each: **$75K/year**

---

## Quick Win #3: Discharge Instruction Template Optimization

**Time to Implement:** 1-2 weeks
**Typical Impact:** 40-60% reduction in discharge instruction completion time
**Evidence:** Common pattern across hospitals - discharge summaries edited 10-20 times before final

### The Problem
Discharge instructions are often:
- Fragmented across multiple screens
- Filled with free-text fields requiring manual typing
- Missing pre-populated common instructions
- Edited by multiple people before completion

### Optimized Design
1. **Single-screen discharge summary**
   - All components on one view: meds, follow-up, activity, diet, red flags

2. **Smart defaults and pick-lists**
   - Common instructions pre-populated based on diagnosis
   - Pick-lists instead of free-text where possible
   - Auto-fill from previous sections (e.g., med list pulls from canonical source)

3. **Role-based workflow**
   - Physician: Diagnosis, clinical instructions
   - Pharmacy: Med reconciliation (auto-populated)
   - Nursing: Patient education confirmation (checkboxes)
   - Everyone sees same document, edits their section

### Implementation Steps
1. **Audit current discharge workflow**
   - Count screens involved: ____
   - Measure edit count per discharge: ____
   - Measure time to completion: ____

2. **Build optimized template**
   - Consolidate into single screen
   - Add smart defaults for top 20 discharge diagnoses
   - Replace free-text with pick-lists where appropriate

3. **Pilot with hospitalist team**
   - 2-week pilot
   - Measure: Time to complete (before vs. after)
   - Measure: Edit count (before vs. after)
   - Survey: Satisfaction

4. **Expand hospital-wide**
   - Staged rollout by service line
   - Monitor incomplete discharge rate

### Expected Outcomes
- **40-60% time reduction** for discharge instructions
- **50-75% fewer edits** before completion
- Reduced patient callbacks for clarification

### Cost
- **Implementation:** 16-24 hours (template design + build)
- **Value:** For 15,000 discharges/year saving 8 min each: **$180K/year** (at $90/hr)

---

## Quick Win #4: Allergy Documentation Single-Source

**Time to Implement:** 1-2 weeks
**Typical Impact:** Eliminate 90%+ of redundant allergy entries
**Evidence:** Safety-critical data should never be re-entered

### The Problem
Allergies are asked and documented:
- Triage
- Nursing admission assessment
- Physician H&P
- Pharmacy verification
- Pre-op assessment

Redundant, error-prone, and wastes time.

### Implementation
1. **Allergy list entered ONCE** (usually at first clinical contact)
2. **Auto-populate everywhere** (show, don't re-ask)
3. **Update in-place if new allergy** (don't create duplicate lists)
4. **Alert on discrepancies** ("Patient reports penicillin allergy, not in chart")

### Expected Outcomes
- **Eliminate 90%+ duplicate entries**
- **Improved safety** (single source = fewer missed allergies)
- **1-2 minutes saved per encounter**

---

## Quick Win #5: Copy-Paste Policy + Training

**Time to Implement:** 1 week
**Typical Impact:** Reduce copy-paste-related errors by 30-50%
**Evidence:** Only 24% of orgs have formal policies (Tsou et al. 2017)

### The Problem
66-90% of clinicians use copy-paste. Copy-paste contributed to:
- 2.6% of all diagnostic errors
- 35.7% of documentation-related diagnostic errors

But: Clinicians use copy-paste because re-entering data is inefficient.

### Balanced Approach
**Don't ban copy-paste.** Instead:

1. **Implement EHR-level safeguards**
   - Highlight copied text
   - Require attestation: "I reviewed and updated this text"
   - Block copy-paste across different patients for certain fields (allergies, problem list)

2. **Reduce need for copy-paste**
   - Auto-populate repeated elements (vitals, med list)
   - Use templates for common documentation patterns
   - Allow "carry forward" for unchanged assessments (with attestation)

3. **Training on safe practices**
   - Never copy-paste: Allergies, problem list, procedure notes
   - Always review and edit: Assessment, plan
   - Safe to copy: Patient demographics, past medical history (if verified)

4. **Audit and feedback**
   - Monthly reports: % notes with >50% copied text
   - Individual feedback to high-copy-paste outliers
   - Tie to quality metrics if patterns linked to errors

### Expected Outcomes
- **30-50% reduction** in copy-paste-related errors
- Maintained efficiency (don't force re-typing)
- Improved note quality

---

## Quick Win #6: After-Hours EHR Work Alerts

**Time to Implement:** 1 week (configuration only)
**Typical Impact:** Visibility into workflow completion problems
**Evidence:** Physicians work 27-34 min/day after-hours on EHR

### The Problem
After-hours EHR work indicates:
- Incomplete handoffs (cleaning up others' work)
- Insufficient in-shift time for documentation
- Workflow inefficiencies requiring catch-up

### Implementation
1. **Configure alerts in EHR analytics**
   - Flag: Users with >30 min/day after-hours EHR work (averaged over week)
   - Dashboard: After-hours trends by department

2. **Weekly manager reports**
   - Send to department leaders
   - Show: Who's working late, how much, on what tasks

3. **Root cause analysis**
   - Interview high after-hours users
   - Ask: "What are you finishing after your shift?"
   - Common findings: Incomplete discharge summaries, unfinished notes, inbox overflow

4. **Targeted interventions**
   - If problem = incomplete handoffs → Workflow redesign
   - If problem = insufficient time → Adjust documentation expectations
   - If problem = inbox overflow → Triage rules, delegation

### Expected Outcomes
- **Visibility into workflow problems** (previously invisible)
- **20-30% reduction** in after-hours work after targeted fixes
- Improved work-life balance (burnout reduction)

---

## Implementation Priority Matrix

| Quick Win | Effort (Hours) | Annual Savings | Payback Period | Safety Impact |
|-----------|----------------|----------------|----------------|---------------|
| Redundant field removal | 24-40 | $300K-500K | <1 month | Low |
| Med rec streamlining | 40-60 | $75K-150K | 2-4 months | **High** |
| Discharge template | 16-24 | $150K-200K | <1 month | Medium |
| Allergy single-source | 16-24 | $50K-100K | 1-2 months | **High** |
| Copy-paste policy | 8-16 | $100K-200K | <1 month | **High** |
| After-hours alerts | 4-8 | Visibility only | N/A | Low |

**Recommended Start Order:**
1. After-hours alerts (easiest, builds case for others)
2. Redundant field removal (high ROI, low risk)
3. Med rec streamlining (high safety impact)
4. Discharge template (high ROI)
5. Allergy single-source (high safety impact)
6. Copy-paste policy (improves quality)

---

## Success Metrics Template

Track weekly for 8 weeks post-implementation:

| Metric | Baseline | Week 4 | Week 8 | Target |
|--------|----------|--------|--------|--------|
| Avg documentation time (min) | ____ | ____ | ____ | -20% |
| Duplicate entries/day | ____ | ____ | ____ | -50% |
| After-hours work (min/day) | ____ | ____ | ____ | -30% |
| Copy-paste error reports | ____ | ____ | ____ | -50% |
| Clinician satisfaction (1-10) | ____ | ____ | ____ | +2 pts |

---

*All ROI calculations assume fully-loaded clinical labor rates: $150/hr physician, $110/hr APP, $90/hr RN. Adjust for your market.*
