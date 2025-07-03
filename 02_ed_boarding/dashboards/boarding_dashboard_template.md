# ED Boarding Real-Time Dashboard Template

## Dashboard Components

### Header Section
- **Hospital Logo & Name**
- **Current Date/Time** (auto-refresh every 5 minutes)
- **Alert Status**: 🟢 Normal | 🟡 Warning | 🔴 Critical

---

### Key Performance Indicators (Top Row)

#### Current ED Status
```
┌─────────────────────┬─────────────────────┬─────────────────────┬─────────────────────┐
│  CURRENT BOARDING   │  AVG BOARDING TIME  │  LONGEST BOARDER   │  ECCQ COMPLIANCE   │
│                     │                     │                     │                    │
│      23 pts         │     4.7 hours       │    18.5 hours      │      76%           │
│    ↑ 15% vs avg     │   ↑ 0.8h from goal  │   🔴 BH Patient     │   ⚠️ Below 90%     │
└─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘
```

---

### Real-Time Boarding Grid

#### Patients Currently Boarding (>2 hours since admission decision)

| Unit Assigned | Patient ID | Hours Boarding | Type | Barriers | Next Action |
|--------------|------------|----------------|------|----------|-------------|
| Medicine A | xxx-01 | 7.5h 🔴 | Medical | No bed | Discharge 2B expedite |
| Psychiatry | xxx-02 | 18.5h 🔴 | BH | Placement | Regional search active |
| Surgery | xxx-03 | 3.2h 🟡 | Surgical | OR backup | Surgery notified |
| Medicine B | xxx-04 | 2.8h 🟡 | Medical | Staff | Float pool requested |

**Color Coding:**
- 🟢 2-4 hours
- 🟡 4-8 hours  
- 🔴 >8 hours

---

### Predictive Analytics Section

#### Next 4 Hours Forecast
```
┌──────────────────────────────────────────────┐
│ PREDICTED ADMISSIONS                         │
│                                              │
│ 2:00 PM - 3:00 PM: 8 admissions expected    │
│ 3:00 PM - 4:00 PM: 12 admissions expected   │
│ 4:00 PM - 5:00 PM: 15 admissions expected   │
│ 5:00 PM - 6:00 PM: 10 admissions expected   │
│                                              │
│ ⚠️ SURGE ALERT: 4-5 PM                       │
└──────────────────────────────────────────────┘
```

#### Discharge Readiness
```
Ready for Discharge NOW: 14 patients
- Medicine: 8
- Surgery: 3  
- Cardiology: 3

Likely Discharge by Noon: 22 patients
```

---

### Unit Capacity View

| Unit | Total Beds | Occupied | Available | Staffed Available | Pending DC |
|------|------------|----------|-----------|-------------------|------------|
| ICU | 24 | 23 | 1 | 0 | 2 |
| Medicine A | 32 | 30 | 2 | 2 | 5 |
| Medicine B | 32 | 31 | 1 | 0 | 3 |
| Surgery | 28 | 25 | 3 | 3 | 4 |
| Psychiatry | 20 | 20 | 0 | 0 | 1 |

**Critical Units**: 🔴 Psychiatry (0 available) | 🔴 ICU (0 staffed available)

---

### Trending Graphs

#### Boarding Hours Trend (Last 7 Days)
```
Hours
8 |    ╱╲
6 |   ╱  ╲    ╱╲
4 |  ╱    ╲__╱  ╲___
2 | ╱              
0 |________________
  Mon Tue Wed Thu Fri Sat Sun
```

#### Hour-by-Hour Heat Map (Today)
```
12am ████░░░░░░░░ Low
6am  ████████░░░░ Medium  
9am  ████████████ High 🔴
12pm ██████████░░ High
3pm  ████████████ Critical 🔴
6pm  ████████░░░░ Medium
9pm  ██████░░░░░░ Medium
```

---

### Action Queue

#### Immediate Actions Required
1. **🔴 Room 4B discharge** - Housekeeping needed (waiting 45 min)
2. **🔴 Psych patient xxx-02** - Escalate to administrator
3. **🟡 Medicine overflow** - Consider hallway placement protocol
4. **🟡 Surgery backlog** - OR schedule review needed

#### Automated Alerts Sent
- ✓ 2:15 PM: Unit managers notified of 4 patients >4h
- ✓ 2:30 PM: House supervisor alert for psych patient >12h
- ✓ 2:45 PM: Staffing office notified of ICU shortage

---

### Footer Metrics Bar
```
Discharge by Noon: 28% | Avg Discharge Lag: 4.2h | Staff Fill Rate: 87% | Last Refresh: 2:47 PM
```

---

## Technical Implementation Notes

### Data Sources Required
1. **ADT System**: Real-time patient location and status
2. **EHR**: Admission decisions, discharge orders
3. **Staffing System**: Current staffing levels
4. **Predictive Model**: API for admission forecasts

### Refresh Rates
- Patient grid: Every 5 minutes
- Predictions: Every 15 minutes
- Capacity: Real-time
- Trends: Every hour

### Alert Logic
```python
if boarding_hours > 8:
    alert_level = "CRITICAL"
    notify = ["administrator", "cno"]
elif boarding_hours > 4:
    alert_level = "WARNING"
    notify = ["house_supervisor"]
elif boarding_hours > 2:
    alert_level = "MONITOR"
    notify = ["unit_manager"]
```

### Display Options
1. **Command Center**: Large wall displays
2. **Mobile**: Responsive design for tablets/phones
3. **Unit Displays**: Focused view for each unit
4. **Executive**: Summary view with KPIs only

---

*This template can be implemented in Tableau, Power BI, or custom web application*