# Power BI Dashboard Template: Discharge by Noon Performance

## Dashboard Overview
This template provides step-by-step instructions to create a comprehensive Discharge by Noon (DBN) dashboard in Power BI with real-time monitoring, predictive analytics, and actionable insights.

## Data Model Setup

### 1. Import Data Sources
```powerquery
// In Power Query Editor, create these queries:

// 1. Patient Encounters
let
    Source = Sql.Database("YourServer", "YourDatabase"),
    PatientEncounters = Source{[Schema="dbo",Item="patient_encounters"]}[Data],
    FilteredRows = Table.SelectRows(PatientEncounters, each [discharge_time] <> null),
    AddedDBNFlag = Table.AddColumn(FilteredRows, "IsDBN", 
        each if Time.Hour([discharge_time]) < 12 then 1 else 0),
    AddedDischargeHour = Table.AddColumn(AddedDBNFlag, "DischargeHour", 
        each Time.Hour([discharge_time]))
in
    AddedDischargeHour

// 2. Units (Dimension table)
let
    Source = Sql.Database("YourServer", "YourDatabase"),
    Units = Source{[Schema="dbo",Item="units"]}[Data]
in
    Units

// 3. Providers (Dimension table)
let
    Source = Sql.Database("YourServer", "YourDatabase"),
    Providers = Source{[Schema="dbo",Item="providers"]}[Data]
in
    Providers
```

### 2. Create Relationships
- patient_encounters[unit_id] → units[unit_id] (Many to One)
- patient_encounters[attending_provider_id] → providers[provider_id] (Many to One)
- Set cross-filter direction to "Single"

### 3. Create Date Table
```dax
DateTable = 
ADDCOLUMNS(
    CALENDAR(
        DATE(2020,1,1),
        TODAY()
    ),
    "Year", YEAR([Date]),
    "Month", FORMAT([Date], "MMM"),
    "MonthNum", MONTH([Date]),
    "Weekday", FORMAT([Date], "ddd"),
    "WeekdayNum", WEEKDAY([Date]),
    "IsWeekend", IF(WEEKDAY([Date]) IN {1,7}, TRUE, FALSE),
    "Quarter", "Q" & QUARTER([Date]),
    "YearMonth", FORMAT([Date], "YYYY-MM")
)
```

## Key Measures

### Core DBN Metrics
```dax
// Total Discharges
Total Discharges = COUNTROWS(patient_encounters)

// DBN Count
DBN Count = CALCULATE(
    [Total Discharges],
    patient_encounters[IsDBN] = 1
)

// DBN Rate
DBN Rate = 
DIVIDE(
    [DBN Count],
    [Total Discharges],
    0
)

// Average Discharge Hour
Avg Discharge Hour = 
AVERAGEX(
    patient_encounters,
    patient_encounters[DischargeHour] + 
    MINUTE(patient_encounters[discharge_time])/60
)

// DBN Target Line (for charts)
DBN Target = 0.30
```

### Trending Metrics
```dax
// Previous Month DBN Rate
Prev Month DBN Rate = 
CALCULATE(
    [DBN Rate],
    PREVIOUSMONTH(DateTable[Date])
)

// DBN Rate Change
DBN Rate Change = [DBN Rate] - [Prev Month DBN Rate]

// 7-Day Moving Average DBN Rate
DBN Rate 7Day MA = 
AVERAGEX(
    DATESINPERIOD(
        DateTable[Date],
        LASTDATE(DateTable[Date]),
        -7,
        DAY
    ),
    [DBN Rate]
)
```

### Performance Categorization
```dax
// DBN Performance Status
DBN Status = 
SWITCH(
    TRUE(),
    [DBN Rate] >= 0.30, "On Target",
    [DBN Rate] >= 0.25, "Near Target",
    [DBN Rate] < 0.25, "Below Target"
)

// DBN Performance Color
DBN Color = 
SWITCH(
    [DBN Status],
    "On Target", "#2E7D32",
    "Near Target", "#F57C00",
    "Below Target", "#C62828"
)
```

### Operational Metrics
```dax
// Weekend DBN Rate
Weekend DBN Rate = 
CALCULATE(
    [DBN Rate],
    DateTable[IsWeekend] = TRUE
)

// Weekday DBN Rate
Weekday DBN Rate = 
CALCULATE(
    [DBN Rate],
    DateTable[IsWeekend] = FALSE
)

// Order to Discharge Lag (minutes)
Avg Order to Discharge = 
AVERAGEX(
    patient_encounters,
    DATEDIFF(
        patient_encounters[discharge_order_time],
        patient_encounters[discharge_time],
        MINUTE
    )
)
```

## Report Pages

### Page 1: Executive Dashboard

#### Layout Components:

**1. KPI Cards (Top Row)**
- Card 1: [DBN Rate] with conditional formatting
- Card 2: [Avg Discharge Hour] formatted as time
- Card 3: [Total Discharges]
- Card 4: [DBN Rate Change] with up/down arrow

**2. DBN Trend Line Chart**
- X-axis: DateTable[Date]
- Y-axis: [DBN Rate]
- Add: [DBN Rate 7Day MA] as second line
- Add: [DBN Target] as constant line
- Enable drill-down by year/month/day

**3. Hourly Distribution Column Chart**
- X-axis: DischargeHour (0-23)
- Y-axis: Count of Encounters
- Conditional formatting: Green (<12), Orange (≥12)
- Add vertical line at hour 12

**4. Unit Performance Matrix**
```dax
// Create matrix visual with:
Rows: units[unit_name]
Values: 
  - [DBN Rate] (with data bars)
  - [Total Discharges]
  - [Avg Discharge Hour]
  
// Add conditional formatting based on [DBN Status]
```

**5. Top Barriers Pareto Chart**
- Use Python visual or custom visual from AppSource
- X-axis: Barrier Category
- Y-axis: Count (bars) and Cumulative % (line)

### Page 2: Operational Analysis

**1. Physician Performance Table**
```dax
// Create table with these fields:
- providers[provider_name]
- providers[specialty]
- [Total Discharges]
- [DBN Rate]
- [Avg Discharge Hour]
- Sparkline: DBN Rate by Month
```

**2. Weekend vs Weekday Comparison**
```dax
// Create clustered column chart:
Category: "Weekend" and "Weekday"
Values: [DBN Rate], [Total Discharges]

// Add these measures:
Weekend Opportunity = 
CALCULATE(
    [Total Discharges],
    DateTable[IsWeekend] = TRUE,
    patient_encounters[IsDBN] = 0,
    patient_encounters[complexity_score] <= 5
)
```

**3. Process Time Waterfall**
- Use waterfall chart to show time components
- Start: Round Time
- Add: Time to Order
- Add: Order to Med Rec
- Add: Med Rec to Transport
- End: Total Process Time

### Page 3: Predictive Analytics

**1. Tomorrow's Predictions**
```dax
// Import prediction results from Python model
// Create measures for:

Predicted DBN Tomorrow = 
CALCULATE(
    COUNTROWS(predictions),
    predictions[prediction_date] = TODAY() + 1,
    predictions[discharge_probability] > 0.5
)

High Confidence Predictions = 
CALCULATE(
    COUNTROWS(predictions),
    predictions[prediction_date] = TODAY() + 1,
    predictions[discharge_probability] > 0.8
)
```

**2. What-If Analysis**
```dax
// Create parameters:
Target DBN Rate = GENERATESERIES(0.20, 0.50, 0.05)
Round Start Hour = GENERATESERIES(7, 10, 0.5)

// Create what-if measures:
Projected Bed Gain = 
VAR TargetRate = SELECTEDVALUE('Target DBN Rate'[Value])
VAR CurrentRate = [DBN Rate]
VAR ImprovementHours = (TargetRate - CurrentRate) * 2
RETURN
    [Total Discharges] * ImprovementHours / 24 / 30

Projected Revenue Impact = 
[Projected Bed Gain] * 8000 * 12  // $8000/admission * 12 months
```

### Page 4: Real-Time Monitoring

**1. Ready for Discharge List**
- Create table showing current patients with:
  - Time since discharge order
  - Predicted discharge time
  - Remaining barriers
  - Priority score

**2. Live Unit Status**
```dax
// Create card visuals for each unit showing:
Current DBN Rate Today = 
CALCULATE(
    [DBN Rate],
    DateTable[Date] = TODAY()
)

Remaining Discharge Potential = 
CALCULATE(
    COUNTROWS(patient_encounters),
    patient_encounters[discharge_order_time] <> BLANK(),
    patient_encounters[discharge_time] = BLANK()
)
```

## Slicers and Filters

### Global Slicers (Sync Across Pages)
1. **Date Range Slicer**
   - Use DateTable[Date]
   - Default: Last 30 days
   - Style: Between

2. **Unit Multi-Select**
   - Use units[unit_name]
   - Default: All selected
   - Style: Dropdown

3. **Provider Multi-Select**
   - Use providers[provider_name]
   - Enable search
   - Style: List

### Page-Specific Filters
1. **Complexity Score Slider** (Page 2)
   - Range: 1-10
   - Default: All

2. **Disposition Type** (Page 2)
   - Home, SNF, Rehab, etc.
   - Style: Buttons

## Conditional Formatting Rules

### DBN Rate Formatting
```dax
// For KPI cards and tables:
If [DBN Rate] >= 0.30 Then Green (#2E7D32)
If [DBN Rate] >= 0.25 Then Yellow (#F57C00)
If [DBN Rate] < 0.25 Then Red (#C62828)
```

### Data Bars
- Apply to DBN Rate in tables
- Min: 0, Max: 0.5
- Gradient from red to green

### Icons
```dax
// Trend indicators:
DBN Trend Icon = 
IF(
    [DBN Rate Change] > 0.02, "⬆️",
    IF([DBN Rate Change] < -0.02, "⬇️", "➡️")
)
```

## Custom Visuals to Import

1. **Pareto Chart** - For barrier analysis
2. **Bullet Chart** - For unit performance vs. target
3. **Gantt Chart** - For discharge timeline visualization
4. **KPI Indicator** - Enhanced KPI cards

## Power BI Service Configuration

### 1. Dataset Refresh
- Schedule refresh every 2 hours during business hours
- Incremental refresh for historical data

### 2. Alerts
```powerbi
// Set up data alerts:
1. DBN Rate falls below 20%
2. Average discharge hour exceeds 2 PM
3. Weekend discharge rate below 10%
```

### 3. Row-Level Security
```dax
// Create RLS roles:
[Unit Manager] = 
PATHCONTAINS(
    units[unit_hierarchy],
    USERPRINCIPALNAME()
)
```

### 4. Mobile Layout
Create phone layout with:
- Single KPI: Today's DBN Rate
- Simple column chart: Last 7 days
- Table: Ready for discharge count by unit

## DAX Optimization Tips

1. **Use Variables**
```dax
Optimized DBN Rate = 
VAR TotalDischarges = COUNTROWS(patient_encounters)
VAR DBNDischarges = CALCULATE(
    TotalDischarges,
    patient_encounters[IsDBN] = 1
)
RETURN
    DIVIDE(DBNDischarges, TotalDischarges, 0)
```

2. **Avoid Bi-Directional Relationships**
   - Keep relationships single-direction
   - Use CROSSFILTER when needed

3. **Pre-calculate in Power Query**
   - IsDBN flag
   - Discharge hour
   - Weekend flag

## Deployment Checklist

- [ ] Validate all measures against SQL queries
- [ ] Test with 90 days of data
- [ ] Configure incremental refresh
- [ ] Set up RLS for unit managers
- [ ] Create mobile layouts
- [ ] Schedule data refresh
- [ ] Set up email subscriptions
- [ ] Configure alerts
- [ ] Document data sources
- [ ] Train end users