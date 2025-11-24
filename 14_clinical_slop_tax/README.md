# Clinical Slop Audit Toolkit

Ready-to-use tools to identify, measure, and eliminate clinical slop in your organization.

## Quick Start

1. **Baseline Audit** → Use the Clinical Slop Assessment Tool
2. **Measure Task-Switching** → Run EHR analytics SQL queries
3. **Analyze Patterns** → Execute Python fragmentation analysis
4. **Visualize Burden** → Build the workflow dashboard
5. **Execute Cleanup** → Follow the optimization playbook

## What's Included

### 📊 SQL Queries (`sql/`)
- EHR task-switching frequency analysis
- Documentation time trending
- Between-chart navigation patterns
- After-hours EHR work measurement
- Redundant data entry detection

### 🐍 Python Analysis (`python/`)
- Clinical slop audit calculator
- Workflow fragmentation analyzer
- Task-switching cost estimator
- Documentation redundancy mapper

### 📈 Dashboard Templates (`dashboards/`)
- Power BI: Clinical Workflow Burden Dashboard
- Tableau: Task-Switching Heatmap Template
- Documentation time trending visualization

### 📋 Implementation Guides (`guides/`)
- Clinical Slop Audit Checklist
- 8-Week Workflow Cleanup Roadmap
- EHR Optimization Quick Wins
- Workflow Ownership Matrix Template

## Key Metrics

This toolkit helps you measure:
- **Task switches per hour** in the EHR (by clinician type)
- **Time spent on documentation** vs. patient care
- **Duplicate data entry instances** across systems
- **After-hours EHR work** patterns
- **Cost of workflow fragmentation**

## Expected Results

Organizations using these tools typically:
- Identify 50-100+ task switches per hour that can be eliminated
- Reduce documentation time by 15-25% through redundancy removal
- Reclaim 20-40 minutes per shift of clinician time
- Reduce after-hours EHR work by 30-50%

## What Is Clinical Slop?

Clinical slop is the unowned, poorly designed, fragmented work that exists because no one owns the workflow end-to-end:

- Hunting through multiple systems for the same information
- Fixing incomplete documentation before acting on it
- Manually reconciling conflicting data
- Re-entering the same information in multiple places
- Chasing down task ownership during handoffs

## Getting Started

```bash
# Run the clinical slop audit
cd python
pip install -r requirements.txt
python clinical_slop_audit.py

# Analyze task-switching patterns
python task_switching_analyzer.py

# Check SQL queries for your EHR
cd ../sql
# Review ehr_task_switching.sql
# Modify for your EHR vendor (Epic, Cerner, etc.)
```

## Use Cases

- **CMIO/CNIO Teams**: Quantify EHR burden and prioritize optimization work
- **Quality/Safety Teams**: Identify error-prone fragmentation points
- **Operations**: Calculate ROI of workflow streamlining initiatives
- **Clinician Well-Being Teams**: Measure burnout drivers and track improvement

## Typical Findings

After running the audit, most organizations discover:

- **30-50%** of documentation elements are duplicated somewhere else
- **15-25%** of EHR time is spent navigating between disconnected systems
- **40-60 minutes per shift** of work exists solely to "fix" incomplete handoffs
- **20-40%** of after-hours work is rework from poor documentation quality

## Quick Wins Checklist

✅ Audit medication reconciliation workflow (usually 3-5 redundant steps)
✅ Map discharge instruction workflow (often involves 4+ systems)
✅ Count task switches during care transitions (handoffs are slop hotspots)
✅ Review copy-paste policy compliance (90% of orgs don't have one)
✅ Measure after-hours documentation work (sign of incomplete handoffs)

## Questions?

See the full article on Vitals & Variables LinkedIn Newsletter for detailed analysis, case studies, and evidence base.

---

*Part of the Vitals & Variables toolkit series - turning healthcare headaches into data-backed fixes.*
