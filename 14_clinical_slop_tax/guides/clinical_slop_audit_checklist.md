# Clinical Slop Audit Checklist

Use this checklist to systematically identify clinical slop in your organization.

## Phase 1: Measurement (Weeks 1-2)

### EHR Analytics

- [ ] **Extract task-switching data** for past 30 days by role
  - Target metrics: Switches per hour, within-chart vs between-chart
  - Use SQL queries from toolkit (ehr_task_switching.sql)

- [ ] **Measure documentation time trends** for past 90 days
  - Target: % time on documentation vs. direct care
  - Flag roles spending >50% on documentation

- [ ] **Quantify after-hours EHR work**
  - Calculate avg minutes/day by role
  - Benchmark: >35 minutes/day = workflow completion problem

### Redundancy Detection

- [ ] **Audit medication reconciliation workflow**
  - Count: How many times is the same medication entered?
  - Common pattern: ED → Admission → Pharmacy → MAR
  - Expected finding: 30-50% of meds duplicated

- [ ] **Review allergy documentation**
  - Check: Are allergies re-entered at each encounter?
  - Should be: Enter once, reference everywhere

- [ ] **Analyze problem list synchronization**
  - Compare: Do departments maintain separate lists?
  - Flag: Problems appearing in >2 departments

### Workflow Fragmentation Points

- [ ] **Map discharge instruction workflow**
  - Count: How many systems/screens involved?
  - Measure: Edit count before completion
  - Benchmark: >10 edits = high fragmentation

- [ ] **Audit care transition documentation**
  - Identify: Which data elements get re-entered during transitions?
  - Common culprits: Chief complaint, HPI, past medical history, social history

- [ ] **Review copy-paste patterns**
  - Measure: % of notes containing copy-pasted text
  - Research benchmark: 66-90% of clinicians use copy-paste
  - Flag: Are copy-paste policies in place?

## Phase 2: Qualitative Assessment (Week 3)

### Clinician Interviews (15-minute structured interviews)

Conduct 10-15 interviews per role (physicians, nurses, APPs).

**Task-Switching Questions:**
- [ ] "How many times per hour do you feel like you're interrupted or switch between tasks in the EHR?"
- [ ] "What EHR workflow forces the most back-and-forth navigation?"
- [ ] "Do you work on the EHR after your shift ends? For how long?"

**Redundancy Questions:**
- [ ] "What information do you find yourself entering more than once?"
- [ ] "Where do you hunt for information that should be in one place?"
- [ ] "Have you ever called a patient back because information was missing or conflicting?"

**Handoff Quality Questions:**
- [ ] "How often do you receive incomplete documentation that requires follow-up?"
- [ ] "What's the most common thing missing during handoffs?"
- [ ] "How much time do you spend 'cleaning up' incomplete work from previous shifts?"

### Observational Time-Motion (Optional but Valuable)

- [ ] **Shadow 5-10 clinicians** for 2-4 hour blocks
  - Log every task switch
  - Note moments where they say "Where is that information?"
  - Count instances of re-entering data
  - Time spent fixing incomplete documentation

## Phase 3: Cost Calculation (Week 4)

### Use Python Audit Tool

- [ ] **Run clinical_slop_audit.py** with your organization's data
  - Input: Task switches/hour, FTE counts, redundant entries/day
  - Output: Annual cost breakdown

### Expected Findings (Typical 400-Bed Hospital)

- **Task-switching cost:** $2-5M/year
- **Redundant documentation:** $500K-1.5M/year
- **Incomplete handoff cleanup:** $300K-800K/year
- **Total clinical slop tax:** $3-7M/year

## Phase 4: Prioritization (Week 4)

### Quick Win Identification

Rank issues by:
1. **Safety risk** (medication errors, care gaps)
2. **Frequency** (happens daily vs. weekly)
3. **Ease of fix** (low-hanging fruit)

Common quick wins:
- [ ] Medication reconciliation streamlining (high impact, moderate effort)
- [ ] Discharge instruction template optimization (high impact, low effort)
- [ ] Redundant EHR fields removal (high impact, low effort)
- [ ] Allergy documentation single-source-of-truth (high impact, moderate effort)

### ROI Calculation

For each prioritized fix:
- [ ] Estimate time savings (minutes/day per clinician)
- [ ] Calculate annual value (savings × FTEs × days/year × hourly rate)
- [ ] Estimate implementation cost (hours + external costs)
- [ ] Calculate payback period

Use `calculate_optimization_roi()` function from audit tool.

## Phase 5: Reporting (Week 4)

### Executive Summary Contents

- [ ] **Total annual clinical slop cost** (single number, bold)
- [ ] **Top 3 slop sources** with individual costs
- [ ] **Benchmark comparison** (your org vs. research benchmarks)
- [ ] **Quick wins list** with ROI projections
- [ ] **Recommended next steps**

### Presentation Tips

- Lead with the total cost number
- Use clinician quotes to make it real
- Show specific examples (med rec workflow diagram)
- Present ROI for top 3 interventions
- End with: "What are we doing this quarter to reduce clinical slop by 20%?"

## Red Flags: When to Escalate Immediately

- [ ] **Task switches >180/hour** for any role (cognitive crisis)
- [ ] **After-hours work >50 minutes/day** on average (workflow failure)
- [ ] **>60% time on documentation** (role inversion - clinicians are data clerks)
- [ ] **Copy-paste errors documented in safety reports** (patient harm occurring)
- [ ] **Clinician quotes include:** "I spend more time in Epic than with patients"

## Common Resistance & Responses

**"Our EHR is fine, it's just how healthcare works now."**
→ Show task-switching comparison: Your org vs. benchmarks

**"We don't have time to fix workflows, we're too busy."**
→ ROI analysis: 200 hours invested returns 30,000 hours annually (Kansas example)

**"The vendor needs to fix this."**
→ Duke Health: 24 hours of internal work, 18.5% reduction. You don't need vendor permission.

**"Clinicians just need more training."**
→ Research shows: 40.4% burnout prevalence related to EHR, all 29 studies linked EHR to stress. It's the system, not the users.

## Resources

- SQL queries: `/sql/ehr_task_switching.sql`, `/sql/redundant_documentation_detector.sql`
- Python calculator: `/python/clinical_slop_audit.py`
- Research citations: See main article README.md

---

*Updated based on peer-reviewed research (Moy et al. 2023, Sinsky et al. 2016, Arndt et al. 2024)*
