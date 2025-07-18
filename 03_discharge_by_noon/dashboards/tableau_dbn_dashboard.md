# Tableau Dashboard Template: Discharge by Noon Performance

## Dashboard Overview
This template creates a comprehensive Discharge by Noon (DBN) monitoring dashboard with real-time metrics, trending, and drill-down capabilities.

## Required Data Sources

### Primary Tables
1. **patient_encounters** - Core patient admission/discharge data
2. **discharge_orders** - Discharge order timing
3. **units** - Hospital unit reference data
4. **providers** - Attending physician data
5. **discharge_barriers** - Barrier tracking (optional)

### Data Connection
```sql
-- Use the provided SQL queries from /sql/discharge_timing_analysis.sql
-- Connect via live connection for real-time updates or extract for performance
```

## Dashboard Layout

### Page 1: Executive Summary

#### KPI Cards (Top Row)
1. **Current DBN Rate**
   - Calculation: `SUM([Is DBN]) / COUNT([Encounter ID]) * 100`
   - Format: Percentage with 1 decimal
   - Color: Green if ≥30%, Yellow if 20-29%, Red if <20%

2. **Average Discharge Hour**
   - Calculation: `AVG([Discharge Hour])`
   - Format: Time (13:45)
   - Reference line at 12:00

3. **Today's Predicted DBN**
   - Link to prediction model output
   - Show confidence interval

4. **Month-over-Month Change**
   - Calculation: Current month vs. previous month DBN rate
   - Format: +/- percentage points

#### Main Visualizations

**1. DBN Trend Chart (Top Left)**
- Line chart showing daily DBN rate over past 90 days
- Include 7-day moving average
- Add reference line at 30% target
- Parameters:
  - X-axis: Discharge Date
  - Y-axis: DBN Rate (%)
  - Color: Performance vs. target

**2. Hourly Distribution (Top Right)**
- Bar chart of discharge times by hour
- Stack by weekday/weekend
- Highlight noon cutoff
- Parameters:
  - X-axis: Hour of Day (0-23)
  - Y-axis: Count of Discharges
  - Color: Before/After Noon

**3. Unit Performance Matrix (Bottom Left)**
- Heatmap or bullet chart by unit
- Show DBN rate and volume
- Sort by performance
- Parameters:
  - Rows: Unit Name
  - Columns: Metrics (DBN Rate, Volume, Avg Hour)
  - Color: Performance scale

**4. Barrier Analysis (Bottom Right)**
- Pareto chart of discharge barriers
- Show frequency and average delay time
- Parameters:
  - X-axis: Barrier Category
  - Y-axis: Count (bar) and Cumulative % (line)

### Page 2: Operational Details

#### Filters (Top)
- Date Range selector
- Unit multi-select
- Physician multi-select
- Disposition type
- Complexity score range

#### Detailed Views

**1. Physician Performance Table**
```
Columns:
- Physician Name
- Specialty
- Total Discharges
- DBN Rate
- Avg Order Time
- Avg Discharge Time
- Trend (sparkline)
```

**2. Weekend vs. Weekday Analysis**
- Side-by-side comparison
- Volume and rate differences
- Opportunity identification

**3. Real-Time Ready List**
- Patients ready for discharge today
- Time since order placed
- Remaining barriers
- Predicted discharge time

**4. Process Time Analysis**
- Waterfall chart showing time components:
  - Round completion to order
  - Order to med rec
  - Med rec to transport
  - Transport to actual discharge

### Page 3: Predictive Analytics

**1. Tomorrow's Discharge Forecast**
- List view with probability scores
- Grouped by unit
- Highlight high-confidence predictions

**2. Capacity Planning View**
- Projected bed availability by hour
- Expected admissions overlay
- Bottleneck identification

**3. What-If Scenario Tool**
- Parameter controls for:
  - Target DBN rate
  - Round start time
  - Process improvements
- Show impact on:
  - Bed availability
  - ED boarding
  - Financial metrics

## Calculated Fields

```tableau
// DBN Flag
IF DATEPART('hour', [Discharge Time]) < 12 THEN 1 ELSE 0 END

// DBN Rate
SUM([DBN Flag]) / COUNT([Encounter ID])

// Discharge Hour Decimal
DATEPART('hour', [Discharge Time]) + DATEPART('minute', [Discharge Time])/60

// Weekend Flag
IF DATEPART('weekday', [Discharge Date]) IN (1,7) THEN 'Weekend' ELSE 'Weekday' END

// Days Since Admission
DATEDIFF('day', [Admission Date], TODAY())

// Order to Discharge Lag (minutes)
DATEDIFF('minute', [Discharge Order Time], [Discharge Time])

// Performance vs Target
[DBN Rate] - 0.30

// Opportunity Score (for identifying improvement targets)
IF [Complexity Score] <= 5 
  AND [Disposition] = 'Home' 
  AND [DBN Flag] = 0 
  AND [Discharge Hour] < 14 
THEN 1 ELSE 0 END
```

## Filters and Parameters

### Global Filters
```tableau
// Date Range Parameter
Name: Date Range
Type: Date Range
Default: Last 30 days

// Unit Filter
Name: Select Units
Type: Multiple Values
Default: All

// Minimum Volume Filter (for physician view)
Name: Minimum Discharges
Type: Integer
Default: 10
Range: 1-50
```

### Dynamic Parameters
```tableau
// DBN Target
Name: DBN Target Rate
Type: Float
Default: 0.30
Range: 0.20 - 0.50

// Time Window for "Ready" List
Name: Hours Since Order
Type: Integer
Default: 2
Range: 1-12
```

## Color Schemes

### Performance Colors
- Exceeds Target (≥30%): #2E7D32 (Green)
- Near Target (25-29%): #F57C00 (Orange)  
- Below Target (<25%): #C62828 (Red)

### Time-based Colors
- Morning (6am-12pm): #4CAF50 (Light Green)
- Afternoon (12pm-6pm): #FF9800 (Orange)
- Evening (6pm-12am): #F44336 (Red)

## Dashboard Actions

### Drill-Down Actions
1. Click unit → Filter to physician view for that unit
2. Click date → Show patient-level detail for that day
3. Click barrier → Display specific cases with that barrier

### Highlight Actions
1. Hover over physician → Highlight their patients in ready list
2. Select time range → Highlight affected units

### URL Actions
1. Click patient → Open EHR to patient chart
2. Click "Export" → Download detailed data for analysis

## Refresh Schedule
- Real-time data: Every 15 minutes during business hours
- Historical metrics: Daily at 2 AM
- Predictions: Every 4 hours

## Mobile Optimization
Create simplified mobile view with:
- Single KPI card (DBN Rate)
- Unit performance list
- Ready for discharge count
- Swipe between units

## Deployment Notes
1. Test with sample data before production deployment
2. Validate calculations against source SQL queries
3. Set up alerts for:
   - DBN rate falling below 20%
   - Unusual discharge patterns
   - Data quality issues
4. Schedule automated email reports for leadership
5. Enable caching for historical data to improve performance