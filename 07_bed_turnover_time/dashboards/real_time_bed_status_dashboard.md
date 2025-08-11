# Real-Time Bed Status Dashboard Template

## Overview
This dashboard provides real-time visibility into bed turnover status, bottlenecks, and performance metrics to optimize patient flow and reduce turnover times.

## Dashboard Components

### 1. Executive Summary Panel (Top)
**Key Metrics (Large Number Cards)**
- Current Bed Occupancy: [XX%]
- Beds in Turnover: [XX]
- Average Turnover Today: [XXX min]
- Beds Ready for Assignment: [XX]

**Traffic Light Indicators**
- Green: <90 minutes
- Yellow: 90-150 minutes  
- Red: >150 minutes

### 2. Real-Time Bed Status Grid (Main View)
**Interactive Bed Map by Unit**
- Visual representation of each bed
- Color coding:
  - Green: Occupied
  - Yellow: In turnover process
  - Blue: Clean and ready
  - Red: Delayed (>90 min in turnover)
  - Gray: Out of service

**Hover Details**
- Bed ID and Room Number
- Current Status
- Time in Current Status
- Last Action Taken
- Next Required Action

### 3. Turnover Pipeline View (Left Panel)
**Waterfall Chart Showing**
- Awaiting Discharge: [XX beds]
- Discharge in Progress: [XX beds]
- Awaiting EVS: [XX beds]
- EVS Cleaning: [XX beds]
- Clean - Awaiting Assignment: [XX beds]
- Assignment in Progress: [XX beds]

**Time Stamps for Each Stage**
- Shows average time and current backlog

### 4. Bottleneck Analysis (Right Panel)
**Real-Time Bottleneck Indicators**
- Longest Waiting Beds (Top 10 list)
- Bottleneck Type Distribution (Pie Chart)
- Units with Most Delays (Bar Chart)

### 5. Trend Analysis (Bottom Panel)
**Time Series Charts**
- Hourly Turnover Volume (Line Chart)
- Average Turnover Time by Hour (Line Chart)
- EVS Response Time Trend (Area Chart)

### 6. Predictive Analytics Panel
**Discharge Predictions**
- Expected Discharges Next 4 Hours
- Predicted EVS Workload
- Recommended Staff Positioning

## Implementation in Tableau

### Data Sources Required
1. **ADT System** (Real-time feed)
   - Patient census
   - Admission/discharge events
   - Bed assignments

2. **EVS System**
   - Work order status
   - Cleaning timestamps
   - Staff assignments

3. **Bed Management System**
   - Bed status updates
   - Assignment queue

### Key Calculations
```
// Average Turnover Time
AVG(DATEDIFF('minute', [Discharge Time], [Next Admission Time]))

// Beds in Delay
COUNT(IF DATEDIFF('minute', [Status Change Time], NOW()) > 90 
     AND [Status] != 'Occupied' THEN [Bed ID] END)

// EVS Response Time
AVG(DATEDIFF('minute', [Discharge Time], [EVS Start Time]))
```

### Refresh Settings
- Data refresh: Every 5 minutes
- Auto-refresh dashboard: Yes
- Cache settings: Minimal (real-time priority)

## Implementation in Power BI

### Data Model
```
Fact_BedStatus
- BedID (Key)
- UnitID (FK)
- CurrentStatus
- StatusChangeTime
- PatientID (FK)

Fact_TurnoverEvents  
- EventID (Key)
- BedID (FK)
- EventType
- EventTimestamp
- StaffID (FK)

Dim_Beds
- BedID (Key)
- RoomNumber
- UnitName
- BedType

Dim_Time
- TimeKey
- Hour
- Minute
- ShiftPeriod
```

### DAX Measures
```DAX
// Current Turnover Time
Current Turnover Minutes = 
DATEDIFF(
    CALCULATE(MAX(Fact_TurnoverEvents[EventTimestamp]),
        Fact_TurnoverEvents[EventType] = "Discharge"),
    NOW(),
    MINUTE
)

// Beds Over Target
Beds Over 90 Min = 
CALCULATE(
    COUNTROWS(Fact_BedStatus),
    FILTER(Fact_BedStatus,
        [Current Turnover Minutes] > 90 &&
        Fact_BedStatus[CurrentStatus] <> "Occupied"
    )
)

// EVS Efficiency Rate
EVS Efficiency = 
DIVIDE(
    CALCULATE(COUNT(Fact_TurnoverEvents[EventID]),
        Fact_TurnoverEvents[EventType] = "Cleaning Complete",
        DATEDIFF(
            RELATED(DischargeTime),
            Fact_TurnoverEvents[EventTimestamp],
            MINUTE) <= 60),
    CALCULATE(COUNT(Fact_TurnoverEvents[EventID]),
        Fact_TurnoverEvents[EventType] = "Cleaning Complete")
)
```

### Power BI Service Configuration
- Dataset refresh: DirectQuery for real-time
- Row-level security: By unit/department
- Mobile layout: Optimized for tablets
- Alerts: Set for beds over 120 min delay

## Alert Configuration

### Critical Alerts (Immediate)
- Any bed in turnover >180 minutes
- EVS queue >10 beds
- Clean beds unassigned >60 minutes

### Warning Alerts (15-min delay)
- Average turnover trending >120 minutes
- Unit-specific bottlenecks forming
- Staffing shortage indicators

### Daily Summary Alerts
- Previous day performance summary
- Overnight turnover issues
- Predicted high-volume periods

## User Roles and Views

### Bed Control
- Full dashboard access
- Ability to update bed status
- Manual override capabilities

### Unit Managers
- Unit-specific view
- Read-only access
- Drill-down to patient level

### EVS Supervisors
- EVS queue focus
- Staff assignment tools
- Performance metrics

### C-Suite
- Executive summary only
- Trend analysis
- Financial impact metrics

## Best Practices

1. **Display Location**
   - Command center: Large wall display
   - Nursing stations: Unit-specific views
   - Mobile devices: Supervisors and managers

2. **Training Requirements**
   - 2-hour initial training for bed control
   - 1-hour training for unit staff
   - Quick reference cards at stations

3. **Change Management**
   - Phase rollout by unit
   - Daily huddle integration
   - Success story sharing

4. **Continuous Improvement**
   - Weekly metric review
   - Monthly dashboard optimization
   - Quarterly user feedback sessions