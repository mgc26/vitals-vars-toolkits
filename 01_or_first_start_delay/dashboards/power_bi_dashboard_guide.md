# Power BI Dashboard Template - First Case On-Time Starts

## Overview
This guide helps you create a FCOTS dashboard in Power BI with key metrics and visualizations.

## Data Model

### Required Tables
1. **FactFirstCases**
   - Date
   - RoomID
   - ScheduledTime
   - ActualInTime
   - DelayMinutes
   - DelayReason
   - SurgeonID
   - ServiceLine

2. **DimSurgeons**
   - SurgeonID
   - SurgeonName
   - Department

3. **DimRooms**
   - RoomID
   - RoomName
   - RoomType

4. **DimDate** (standard date table)

## Key Measures (DAX)

```dax
// Overall FCOTS %
FCOTS % = 
DIVIDE(
    CALCULATE(COUNTROWS(FactFirstCases), FactFirstCases[DelayMinutes] <= 0),
    COUNTROWS(FactFirstCases),
    0
) * 100

// Average Delay When Late
Avg Delay When Late = 
CALCULATE(
    AVERAGE(FactFirstCases[DelayMinutes]),
    FactFirstCases[DelayMinutes] > 0
)

// Total Delay Hours
Total Delay Hours = 
SUMX(
    FILTER(FactFirstCases, FactFirstCases[DelayMinutes] > 0),
    FactFirstCases[DelayMinutes] / 60
)

// Monthly Trend
Monthly FCOTS % = 
CALCULATE(
    [FCOTS %],
    DATESMTD(DimDate[Date])
)

// Financial Impact
Delay Cost = [Total Delay Hours] * 100 * 60  // $100/min
```

## Dashboard Layout

### Page 1: Executive Summary

**Top Row - KPI Cards:**
1. Current Month FCOTS % (Big number, conditional formatting: Red <75%, Yellow 75-84%, Green ≥85%)
2. MTD Delay Cost
3. Average Delay (minutes)
4. YTD Improvement %

**Middle Section:**
1. **Line Chart**: Daily FCOTS % with 30-day moving average
   - X-axis: Date
   - Y-axis: FCOTS %
   - Reference line at 85%
   
2. **Column Chart**: Delay Reasons Pareto
   - X-axis: Delay Reason
   - Y-axis: Count of Delays
   - Secondary axis: Cumulative %

**Bottom Section:**
1. **Table**: Surgeon Scorecard
   - Columns: Surgeon, Cases, FCOTS %, Avg Delay, Trend
   - Conditional formatting on FCOTS %
   - Sparkline for trend

### Page 2: Operational Details

**Filters**: Date range, Service line, Room

**Visualizations:**
1. **Heatmap**: Room Performance by Day of Week
2. **Waterfall Chart**: Improvement Journey (baseline to current)
3. **Scatter Plot**: Volume vs Performance by Surgeon
4. **Table**: Tomorrow's First Cases with readiness status

### Page 3: Financial Impact

1. **Area Chart**: Cumulative cost savings vs target
2. **Gauge**: Current month savings progress
3. **Table**: ROI breakdown by intervention

## Power BI Service Setup

### Scheduled Refresh
1. Connect to your data warehouse
2. Set refresh schedule: Daily at 5:00 AM
3. Enable failure notifications

### Row-Level Security
```dax
// Surgeons see only their data
[SurgeonEmail] = USERPRINCIPALNAME()
```

### Alerts
1. FCOTS % drops below 80%
2. Single day delay cost exceeds $10K
3. Any surgeon below 70% for the week

## Mobile Layout
Create phone layout focusing on:
- Today's FCOTS %
- Top 3 delay reasons
- Surgeon ranking

## Quick Start Steps

1. **Import Data**
   - Connect to your EMR/data warehouse
   - Or use the sample CSV for testing

2. **Create Relationships**
   - FactFirstCases[SurgeonID] → DimSurgeons[SurgeonID]
   - FactFirstCases[RoomID] → DimRooms[RoomID]
   - FactFirstCases[Date] → DimDate[Date]

3. **Build Measures**
   - Copy DAX formulas above
   - Create measure table for organization

4. **Design Pages**
   - Use layout guide above
   - Apply your hospital's color scheme

5. **Publish & Share**
   - Publish to Power BI Service
   - Create workspace for OR team
   - Set up email subscriptions

## Tips
- Pre-filter to last 90 days for performance
- Use bookmarks for different views (Executive, Operational, Surgeon)
- Create "What-If" parameter for target FCOTS % scenarios
- Pin key visuals to OR Management dashboard