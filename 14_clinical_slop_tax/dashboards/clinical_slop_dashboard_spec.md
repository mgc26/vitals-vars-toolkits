# Clinical Slop Dashboard Specification

Technical specification for building a Clinical Workflow Burden Dashboard in Power BI or Tableau.

## Dashboard Purpose

Real-time monitoring of clinical slop metrics to identify workflow fragmentation, track optimization initiatives, and prevent clinician burnout.

**Primary Users:** CMIO, CNIO, COO, Clinical Informatics Teams, Department Leaders

---

## Data Sources

### Required Tables/Views
1. **EHR Audit Log** (event-level clinician activity)
   - Fields: user_id, timestamp, activity_type, module_name, patient_id, time_spent_seconds
2. **Clinical Documentation** (note metadata)
   - Fields: note_id, author_id, note_type, timestamp, edit_count, completion_time
3. **Medication Documentation** (for redundancy tracking)
   - Fields: patient_id, encounter_id, medication, source_system, timestamp
4. **User Metadata** (clinician details)
   - Fields: user_id, role, department, shift_schedule, FTE_status

### Refresh Frequency
- **Real-time:** After-hours work alerts (refresh every 15 minutes)
- **Daily:** Task-switching metrics, documentation time
- **Weekly:** Trend analysis, ROI tracking

---

## Page 1: Executive Summary

### KPIs (Top of Page)
Display 4 large summary metrics with trend indicators:

1. **Total Annual Clinical Slop Cost**
   - Calculation: (Task-switching cost + Redundancy cost + Incomplete handoff cost)
   - Format: $X.XM
   - Trend: vs. prior month

2. **Avg Task Switches per Hour (Organization-wide)**
   - Calculation: SUM(task_switches) / SUM(active_hours)
   - Format: XXX switches/hour
   - Color code:
     - Green: <100
     - Yellow: 100-150
     - Red: >150

3. **Documentation Time %**
   - Calculation: Documentation_hours / Total_EHR_hours
   - Format: XX%
   - Benchmark comparison: Research standard 40-50%

4. **After-Hours Work Average**
   - Calculation: AVG(after_hours_minutes) per clinician per day
   - Format: XX minutes/day
   - Benchmark: >35 min/day = concerning

### Alert Section
- **Red flags this week:** (auto-populated list)
  - Departments with >180 switches/hour
  - Individuals with >50 min/day after-hours work
  - New safety events linked to documentation

### Trend Chart
- **Line chart:** 12-week trend of all 4 KPIs
- **X-axis:** Week
- **Y-axis:** Dual axis (cost on left, switches/% on right)
- **Annotations:** Mark optimization initiative launch dates

---

## Page 2: Task-Switching Deep Dive

### Visual 1: Task Switches by Role (Bar Chart)
- **X-axis:** Role (Physician, Nurse, APP, etc.)
- **Y-axis:** Avg switches per hour
- **Benchmark line:** 100 switches/hour (acceptable threshold)
- **Color:** Gradient (green <100, yellow 100-150, red >150)
- **Drill-through:** Click role → go to department breakdown

### Visual 2: Within-Chart vs Between-Chart Switching (Stacked Bar)
- **X-axis:** Role
- **Y-axis:** Count of switches
- **Segments:**
  - Within-chart (jumping between tabs for same patient)
  - Between-chart (switching patients)
- **Insight:** High within-chart = poor EHR design

### Visual 3: Task-Switching Heatmap (Calendar View)
- **Rows:** Hour of day (0-23)
- **Columns:** Day of week
- **Color intensity:** Avg task switches per hour during that time block
- **Use:** Identify peak fragmentation periods

### Visual 4: High-Fragmentation Individuals (Table)
- **Columns:**
  - User ID (anonymized if needed)
  - Role
  - Department
  - Avg switches/hour (last 30 days)
  - Days worked
  - After-hours work (min/day)
- **Filter:** Show top 50 by switches/hour
- **Use:** Targeted intervention outreach

### Filters
- Date range (default: last 30 days)
- Department
- Role
- Shift type (day/night)

---

## Page 3: Documentation Burden

### Visual 1: Time Allocation by Role (Stacked Bar)
- **X-axis:** Role
- **Y-axis:** % of EHR time
- **Segments:**
  - Documentation/Note Writing
  - Chart Review
  - Ordering
  - Inbox Management
  - Other
- **Benchmark line:** 40% documentation (acceptable threshold)

### Visual 2: Documentation Time Trend (Line Chart)
- **X-axis:** Week
- **Y-axis:** % time on documentation
- **Lines:** One per role
- **Annotations:** Mark optimization initiatives (e.g., "Redundant fields removed")

### Visual 3: After-Hours Work Distribution (Histogram)
- **X-axis:** After-hours minutes per day (bins: 0-10, 10-20, ... 60+)
- **Y-axis:** Count of clinicians
- **Color:** By role
- **Insight:** How many clinicians are working excessive after-hours?

### Visual 4: After-Hours Work by Department (Bar Chart)
- **X-axis:** Department
- **Y-axis:** Avg after-hours minutes per clinician per day
- **Benchmark line:** 35 minutes (concerning threshold)
- **Drill-through:** Click department → see individual users

### Filters
- Date range
- Department
- Role

---

## Page 4: Workflow Fragmentation Hotspots

### Visual 1: Module Navigation Sankey Diagram
- **Flow:** Shows most common EHR module transitions
- **Example:** Orders → Medications → Notes → Orders (circular pattern = inefficiency)
- **Width of line:** Frequency of transition
- **Use:** Identify navigation patterns requiring too many clicks

### Visual 2: Top 10 Redundant Data Elements (Bar Chart)
- **X-axis:** Data element (e.g., "Medication List", "Allergies", "Problem List")
- **Y-axis:** Count of duplicate entries per month
- **Color:** By source system
- **Use:** Prioritize single-source-of-truth initiatives

### Visual 3: Incomplete Handoff Rate by Department (Bar Chart)
- **X-axis:** Department
- **Y-axis:** % of handoffs requiring downstream cleanup
- **Benchmark line:** 20% (typical baseline)
- **Color:** Red if >30%

### Visual 4: Copy-Paste Frequency (Line + Table)
- **Line chart:** % of notes with copy-paste over time
- **Table:** Top 10 users by copy-paste %
- **Benchmark:** 70% (research average)
- **Use:** Track policy compliance after intervention

---

## Page 5: ROI Tracking

### Visual 1: Optimization Initiatives Timeline (Gantt Chart)
- **Rows:** Initiative name (e.g., "Redundant Field Removal - Med/Surg")
- **Columns:** Timeline
- **Color:** Status (Planning, In Progress, Completed)
- **Milestones:** Implementation date, measurement dates

### Visual 2: Cost Savings by Initiative (Waterfall Chart)
- **X-axis:** Baseline → Initiative 1 → Initiative 2 → ... → Current
- **Y-axis:** Annual clinical slop cost
- **Bars:** Show decrease from each initiative
- **Use:** Visualize cumulative impact

### Visual 3: Initiative Impact Comparison (Scatter Plot)
- **X-axis:** Implementation cost (hours)
- **Y-axis:** Annual savings ($)
- **Size of bubble:** Time to payback
- **Color:** By initiative type
- **Use:** Identify best ROI opportunities

### Visual 4: Before/After Metrics Table
- **Rows:** Each optimization initiative
- **Columns:**
  - Metric (e.g., "Task switches/hour")
  - Baseline
  - Current
  - Change (%)
  - Target
  - Status (on track / at risk)

---

## Page 6: Clinician Well-Being Proxy

**Note:** This page uses EHR behavior as proxy for burnout risk.

### Visual 1: Burnout Risk Score by Department (Gauge Chart)
- **Risk Score Calculation:**
  - Task switches >150/hr: +3 points
  - Documentation >50%: +2 points
  - After-hours >40 min/day: +3 points
  - Total: 0-8 scale
- **Display:** Gauge for each department
- **Color:** Green (0-2), Yellow (3-5), Red (6-8)

### Visual 2: High-Risk Individual Count (Card Visual)
- **Metric:** Count of clinicians with burnout risk score ≥6
- **Trend:** vs. prior month
- **Use:** Escalation trigger for leadership

### Visual 3: Risk Factor Breakdown (Stacked Bar)
- **X-axis:** Department
- **Y-axis:** Count of clinicians
- **Segments:** By dominant risk factor (task-switching, documentation, after-hours)

### Visual 4: Intervention Priority List (Table)
- **Columns:**
  - Department
  - Risk score
  - Primary issue
  - Recommended intervention
  - Est. cost savings
- **Sorted by:** Risk score descending

---

## Alerting Rules

Set up automated alerts (email/Slack) for:

1. **Critical Threshold Breaches**
   - Any role with avg >180 task switches/hour for 3+ consecutive days
   - Any department with >60% time on documentation
   - Individual user with >60 min/day after-hours work for 5+ days

2. **Trend Deterioration**
   - Week-over-week increase >10% in any KPI
   - Month-over-month increase >20% in clinical slop cost

3. **Safety-Related**
   - Copy-paste error reported in safety system
   - Medication reconciliation discrepancy rate >10%

---

## Technical Implementation Notes

### Power BI
- **Data source:** Direct Query to SQL database for real-time
- **Refresh schedule:** Daily at 6 AM for aggregated metrics
- **Security:** Row-level security by department (managers see only their dept)
- **Export:** Allow export of aggregate data, not individual-level

### Tableau
- **Data source:** Hyper extracts for performance
- **Refresh schedule:** Daily refresh of last 90 days
- **Parameters:** Allow users to set custom thresholds (e.g., their org's "concerning" switches/hour)
- **Subscriptions:** Weekly email snapshots to leadership

### Data Quality Checks
- **Missing data alerts:** If >10% of EHR audit log missing timestamps/user_ids
- **Outlier detection:** Flag users with >500 switches/hour (likely data error)
- **Validation:** Cross-check documentation time with payroll hours

---

## Dashboard Maintenance

### Weekly
- Review alerts, escalate critical issues
- Validate data quality
- Update initiative statuses

### Monthly
- Review with CMIO/CNIO
- Adjust thresholds if organizational goals change
- Add new departments as they opt in

### Quarterly
- Benchmark against industry standards (update research targets)
- Audit ROI calculations (actual vs. projected)
- Refresh user training on dashboard

---

## Expected Usage Patterns

**Daily:** Operations teams monitoring alerts
**Weekly:** Department leaders reviewing their metrics
**Monthly:** Executive team reviewing trends and ROI
**Quarterly:** Strategic planning for next optimization initiatives

---

*This specification is based on proven clinical analytics dashboard designs. Adapt data fields and calculations to your EHR vendor's data model.*
