# Tableau Dashboard Template - First Case On-Time Starts

## Overview
Build an interactive FCOTS dashboard in Tableau with drill-down capabilities and real-time monitoring.

## Data Connection

### Option 1: Direct Database Connection
```sql
-- Custom SQL Query for Tableau
SELECT 
    c.surgery_date,
    c.room_id,
    c.scheduled_time,
    c.actual_in_time,
    c.delay_minutes,
    c.delay_reason,
    c.surgeon_id,
    s.surgeon_name,
    s.department,
    r.room_name,
    CASE 
        WHEN c.delay_minutes <= 0 THEN 1 
        ELSE 0 
    END as on_time_flag,
    CASE 
        WHEN c.delay_minutes <= 0 THEN 'On Time'
        WHEN c.delay_minutes <= 15 THEN '1-15 min late'
        WHEN c.delay_minutes <= 30 THEN '16-30 min late'
        ELSE '>30 min late'
    END as delay_category
FROM first_cases c
LEFT JOIN surgeons s ON c.surgeon_id = s.surgeon_id
LEFT JOIN rooms r ON c.room_id = r.room_id
WHERE c.surgery_date >= DATEADD(day, -90, GETDATE())
```

### Option 2: Excel/CSV Import
Use provided sample data or export from EMR

## Calculated Fields

```tableau
// FCOTS Percentage
[FCOTS %]: 
SUM([On Time Flag]) / COUNT([Case ID]) * 100

// Average Delay When Late
[Avg Delay When Late]:
IF SUM([Number of Records]) > 0 THEN
    SUM(IF [Delay Minutes] > 0 THEN [Delay Minutes] END) / 
    SUM(IF [Delay Minutes] > 0 THEN 1 END)
END

// Delay Cost
[Delay Cost]:
SUM(IF [Delay Minutes] > 0 THEN [Delay Minutes] * 100 ELSE 0 END)

// Days Since Implementation
[Days Since Start]:
DATEDIFF('day', #2024-01-01#, [Surgery Date])

// Moving Average FCOTS
[MA30 FCOTS]:
WINDOW_AVG([FCOTS %], -29, 0)

// Performance Tier
[Performance Tier]:
IF [FCOTS %] >= 90 THEN "Exceeds Target"
ELSEIF [FCOTS %] >= 85 THEN "Meets Target"  
ELSEIF [FCOTS %] >= 75 THEN "Approaching"
ELSE "Needs Improvement"
END
```

## Dashboard Components

### Sheet 1: KPI Summary
- **FCOTS % (BAN)**: Big number with arrow showing trend
- **Cost Impact (BAN)**: Monthly delay cost
- **Cases Analyzed (BAN)**: Total first cases
- **Top Delay Reason (BAN)**: Most common cause

### Sheet 2: Trend Analysis
**Dual-Axis Line Chart**
- Rows: [FCOTS %], [MA30 FCOTS]
- Columns: [Surgery Date] (continuous)
- Reference line at 85%
- Forecast for next 30 days

### Sheet 3: Delay Reasons Pareto
**Combination Chart**
- Columns: [Delay Reason] sorted by count DESC
- Rows: COUNT([Case ID]) (bar)
- Secondary axis: Running sum of % of total (line)
- Filter: Exclude "On Time"

### Sheet 4: Surgeon Scorecard
**Highlight Table**
- Rows: [Surgeon Name]
- Columns: [Performance Tier]
- Color: [FCOTS %]
- Label: Cases count
- Sort by FCOTS % ascending

### Sheet 5: Room Heatmap
**Calendar Heatmap**
- Columns: WEEKDAY([Surgery Date])
- Rows: [Room Name]
- Color: [FCOTS %]
- Label: [Delay Minutes]

### Sheet 6: Financial Impact
**Area Chart**
- Cumulative delay cost over time
- Reference line for budget target
- Annotation for major improvements

## Dashboard Layout

### Main Dashboard (1200x800)

```
+------------------+------------------+------------------+------------------+
|   FCOTS % BAN    | Cost Impact BAN  |  Cases BAN       | Top Delay BAN    |
+------------------+------------------+------------------+------------------+
|                                                                            |
|                    Trend Analysis (dual axis line chart)                   |
|                                                                            |
+----------------------------------------+-----------------------------------+
|                                        |                                   |
|     Delay Reasons Pareto               |     Room Heatmap                  |
|                                        |                                   |
+----------------------------------------+-----------------------------------+
|                                                                            |
|                         Surgeon Scorecard Table                            |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Filters & Parameters

**Global Filters:**
- Date Range (default: Last 90 days)
- Service Line
- Surgeon (multi-select)
- Room (multi-select)

**Parameters:**
- Target FCOTS % (default: 85)
- Cost per minute (default: 100)
- Forecast periods (default: 30)

## Interactive Features

### Actions
1. **Filter on Surgeon**: Click surgeon in scorecard → filters all sheets
2. **Highlight Delay Reason**: Hover on Pareto → highlights in other views
3. **Drill to Details**: Click any mark → shows case-level details

### Tooltips
```
<Sheet name>
Date: <Surgery Date>
Room: <Room Name>
Surgeon: <Surgeon Name>
Scheduled: <Scheduled Time>
Actual: <Actual In Time>
Delay: <Delay Minutes> minutes
Reason: <Delay Reason>
Cost Impact: $<Delay Cost>
```

## Mobile Layout
Create phone layout with:
1. Today's FCOTS % (large)
2. Week trend sparkline
3. Top 3 delay reasons
4. Surgeon rankings (top 5 and bottom 5)

## Publishing & Alerts

### Tableau Server/Online
1. Publish to "OR Operations" project
2. Set extract refresh: Daily 5 AM
3. Subscribe key users to morning email

### Alerts
Create data-driven alerts for:
- FCOTS % below 80% for any day
- Any surgeon below 70% for the week
- Delay cost exceeding $15K/day

## Advanced Features

### Set Actions
Create surgeon sets for:
- "Champions" (≥90% FCOTS)
- "Focus Group" (<75% FCOTS)

### Level of Detail (LOD) Expressions
```tableau
// Surgeon's Best Day
{ FIXED [Surgeon Name] : MAX([FCOTS %]) }

// Room Baseline
{ FIXED [Room Name] : AVG(
    IF [Surgery Date] < #2024-01-01# 
    THEN [FCOTS %] END
)}
```

### Forecasting
- Apply exponential smoothing to trend
- Show confidence bands
- Predict when 90% target achieved

## Quick Start

1. **Connect** to data source (database or CSV)
2. **Create** calculated fields (copy from above)
3. **Build** individual sheets
4. **Assemble** dashboard using layout guide
5. **Add** interactivity and filters
6. **Publish** and schedule refresh
7. **Train** users on mobile app

## Tips
- Use hospital brand colors
- Keep marks under 1000 for performance
- Pre-aggregate data if >100K rows
- Create bookmarks for common views
- Use story points for monthly review presentation