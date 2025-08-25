# Staffing Variance Dashboard Specifications

## Overview
Real-time dashboard for monitoring and managing staffing variance across all units.

## Dashboard Components

### 1. Executive Summary Panel (Top)
**Metrics:**
- Current Variance: XX% (color-coded: green <8%, yellow 8-15%, red >15%)
- Weekly Excess Cost: $XX,XXX
- Units Understaffed Now: X of XX
- Overtime Hours Today: XXX hrs
- Agency Hours Today: XXX hrs

**Time Period Selector:** Today | This Week | This Month | Custom

### 2. Real-Time Unit Status Grid (Left Panel)

| Unit | Census | Required | Actual | Variance | Status | Action |
|------|--------|----------|--------|----------|--------|--------|
| ICU-1 | 12 | 6 | 5 | -1 | 🔴 Under | Request |
| Med-Surg-2 | 24 | 6 | 7 | +1 | 🟡 Over | Available |
| ED | 32 | 8 | 8 | 0 | 🟢 OK | - |

**Color Coding:**
- 🔴 Red: Understaffed (actual < required)
- 🟡 Yellow: Overstaffed (actual > required * 1.1)
- 🟢 Green: Adequately staffed

### 3. Variance Trend Chart (Center)
**Chart Type:** Line chart with dual axis
- **Primary Axis:** Staffing variance percentage
- **Secondary Axis:** Census
- **Time Range:** Last 30 days with daily granularity
- **Lines:**
  - Actual variance (blue)
  - Target variance threshold (green dashed at 8%)
  - Census trend (gray area)

### 4. Day of Week Pattern Analysis (Right Panel)
**Chart Type:** Grouped bar chart
- **X-Axis:** Days of week
- **Y-Axis:** Average variance %
- **Bars:**
  - Monday (highlight in red if >15%)
  - Other days (blue)
  - Include data labels

### 5. Cost Impact Tracker (Bottom Left)
**Metrics Table:**

| Category | This Week | Last Week | Trend |
|----------|-----------|-----------|-------|
| Overtime Premium | $XX,XXX | $XX,XXX | ↑/↓ X% |
| Agency Premium | $XX,XXX | $XX,XXX | ↑/↓ X% |
| Total Excess | $XX,XXX | $XX,XXX | ↑/↓ X% |

**Gauge Chart:** Weekly savings vs target

### 6. Predictive Alert Panel (Bottom Center)
**Tomorrow's Forecast:**
- Predicted census: XXX
- Recommended staff: XX
- Current scheduled: XX
- Gap/Surplus: +/- X
- Risk level: Low/Medium/High

**Next 7 Days Heat Map:**
- Grid showing predicted variance by unit and day
- Color intensity indicates severity

### 7. Rebalancing Opportunities (Bottom Right)
**Live Recommendations:**
```
✓ Move 1 nurse from Med-Surg-2 to ICU-1
✓ Call flex pool for ED (2 nurses needed)
✓ Release 1 nurse early from Unit-4
```

## Technical Specifications

### Data Sources
- **Primary:** Staffing management system (real-time API)
- **Secondary:** Census/ADT system (15-minute updates)
- **Tertiary:** Payroll system (daily batch)

### Refresh Rates
- Unit status grid: Every 15 minutes
- Variance trends: Hourly
- Cost metrics: Daily at 6 AM
- Predictions: Daily at 5 AM, 1 PM

### Filters
- **Unit Type:** ICU | Med-Surg | ED | Telemetry | All
- **Shift:** Day | Evening | Night | All
- **Date Range:** Custom selector

### Drill-Down Capabilities
Click any unit to see:
- 24-hour staffing timeline
- Individual staff assignments
- Overtime/agency detail
- Historical patterns for that unit

### Alerts & Notifications
**Real-Time Alerts:**
- Variance exceeds 20% on any unit
- Multiple units understaffed simultaneously
- Overtime hours exceed daily threshold
- Monday surge not adequately covered

**Alert Channels:**
- Dashboard banner
- Email to managers
- Text to staffing coordinator
- Mobile app push notification

## Power BI Implementation

```DAX
// Key Measures

Variance % = 
DIVIDE(
    SUM(Staffing[Actual]) - SUM(Staffing[Required]),
    SUM(Staffing[Required]),
    0
) * 100

Excess Cost = 
SUM(Staffing[OvertimeHours]) * (67.50 - 45) +
SUM(Staffing[AgencyHours]) * (110 - 45)

Units Understaffed = 
COUNTROWS(
    FILTER(
        Units,
        [Actual Staff] < [Required Staff]
    )
)
```

## Tableau Implementation

```sql
-- Variance Calculation
(SUM([Actual Staff]) - SUM([Required Staff])) / SUM([Required Staff]) * 100

-- Status Indicator
IF [Variance %] < -5 THEN "Understaffed"
ELSEIF [Variance %] > 10 THEN "Overstaffed"
ELSE "Adequate"
END

-- Rebalancing Opportunities
IF [Unit A Variance] > 1 AND [Unit B Variance] < -1 
THEN "Move staff from " + [Unit A] + " to " + [Unit B]
END
```

## Mobile Companion View
Simplified mobile dashboard showing:
1. Current shift status (red/yellow/green units)
2. Immediate actions needed
3. Next shift predictions
4. One-touch rebalancing approval

## Success Metrics
- Reduce average variance from 18% to <8%
- Decrease overtime hours by 60%
- Improve manager response time to <30 minutes
- Achieve 90% forecast accuracy

## Implementation Timeline
- Week 1-2: Connect data sources
- Week 3: Build core visualizations
- Week 4: Add predictive components
- Week 5: Mobile optimization
- Week 6: User training and go-live