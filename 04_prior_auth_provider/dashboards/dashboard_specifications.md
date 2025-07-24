# Prior Authorization Dashboard Specifications

## Overview

This document provides specifications for building prior authorization dashboards in your preferred BI tool (Power BI, Tableau, or similar). Use these requirements with the SQL queries provided in the `sql/` folder.

## Dashboard Components

### 1. Executive Summary Dashboard

**Purpose:** C-suite view of PA performance and financial impact

**Key Metrics (KPIs at top):**
- Current Month Denial Rate % (with trend arrow)
- Administrative Surrender $ (monthly and YTD)
- Average TAT in days (with target line at 1 day)
- First-Pass Approval Rate % (with 90% target line)

**Visualizations:**
- **Denial Trend Chart:** 12-month line chart showing denial rate % by month
- **Payer Performance Matrix:** Heat map showing denial rates by payer (use denial_hotspot_analysis.sql)
- **Revenue at Risk:** Stacked bar chart showing appealed vs. surrendered revenue
- **Service Line Comparison:** Horizontal bar chart of denial rates by department

**Filters:**
- Date range selector
- Payer multi-select
- Service line multi-select

### 2. Operational Dashboard

**Purpose:** Daily management tool for PA team leaders

**Key Metrics:**
- Requests in Queue (aging buckets: 0-24hrs, 24-48hrs, 48-72hrs, 72hrs+)
- Today's Completed Authorizations
- P2P Requests Pending
- Staff Productivity (auths per FTE)

**Visualizations:**
- **Real-Time Queue:** Table showing all pending requests with:
  - Patient ID (masked)
  - Procedure
  - Payer
  - Hours waiting
  - Assigned specialist
  - Risk score (from complexity scorer)
- **Bottleneck Analysis:** Funnel chart showing where requests get stuck
- **Staff Performance:** Bar chart of authorizations completed by team member
- **Hourly Volume:** Line chart showing request volume by hour of day

**Alerts:**
- Requests approaching payer deadline (highlight in red)
- High-risk requests without review (highlight in orange)
- Staff productivity below threshold

### 3. Denial Analysis Dashboard

**Purpose:** Identify patterns and improvement opportunities

**Key Metrics:**
- Top 5 Denial Reasons (% of total)
- Appeal Success Rate %
- Documentation-Related Denials %
- Average Days to Appeal

**Visualizations:**
- **Denial Reasons Pareto:** Bar + line chart showing cumulative impact
- **CPT Code Analysis:** Bubble chart (x=volume, y=denial rate, size=revenue)
- **Payer Denial Patterns:** Grouped bar chart by denial reason and payer
- **Time-to-Denial:** Histogram showing distribution of TAT for denials

**Drill-Down Capability:**
- Click any denial reason → see specific cases
- Click any CPT code → see documentation requirements
- Click any payer → see historical performance

### 4. ROI Tracking Dashboard

**Purpose:** Demonstrate value of PA improvements

**Key Metrics:**
- Revenue Recovered This Month
- Denials Prevented (vs. baseline)
- Physician Hours Saved
- ROI % (actual vs. projected)

**Visualizations:**
- **Recovery Trend:** Area chart showing cumulative recovery
- **Before/After Comparison:** Side-by-side bar charts
- **ROI Waterfall:** Show components of value creation
- **Physician Time Savings:** Gauge showing hours returned to clinical care

## Data Requirements

### Core Tables Needed:
1. **Authorization Requests**
   - Request ID, Date, Patient ID, CPT Code, Payer, Status
2. **Claims**
   - Claim ID, Authorization ID, Amount, Status, Denial Reason
3. **Payers**
   - Payer ID, Name, Type
4. **Providers/Staff**
   - Provider ID, Name, Department, Role

### Update Frequency:
- Executive Dashboard: Daily refresh
- Operational Dashboard: Real-time or hourly
- Analysis Dashboards: Daily refresh
- ROI Dashboard: Weekly refresh

## Implementation Tips

1. **Start Simple:** Build the Executive Dashboard first
2. **Use Existing Queries:** Leverage the SQL provided in this toolkit
3. **Mobile Responsive:** Ensure executives can view on tablets/phones
4. **Export Capability:** Add PDF/Excel export for reporting
5. **Row-Level Security:** Implement based on user department/role

## Color Coding Standards

- **Green:** Meeting or exceeding target
- **Yellow:** Within 10% of target
- **Red:** More than 10% below target
- **Blue:** Neutral/informational

## Sample DAX/Calculated Fields (Power BI)

```dax
Administrative Surrender = 
CALCULATE(
    SUM(Claims[Amount]),
    Claims[Status] = "Denied",
    Claims[Appealed] = "No",
    Claims[DenialReason] CONTAINS "Authorization"
)

Denial Rate % = 
DIVIDE(
    COUNTROWS(FILTER(Claims, Claims[Status] = "Denied")),
    COUNTROWS(Claims),
    0
) * 100

Days Outstanding = 
DATEDIFF(
    AuthorizationRequests[RequestDate],
    TODAY(),
    DAY
)
```

## Next Steps

1. Work with your BI team to implement these specifications
2. Start with one dashboard and iterate based on user feedback
3. Schedule weekly reviews during first month of implementation
4. Refine metrics based on your organization's specific needs

---

*Note: Full Power BI and Tableau template files will be available in a future toolkit update. These specifications provide everything needed to build the dashboards using your existing BI infrastructure.*