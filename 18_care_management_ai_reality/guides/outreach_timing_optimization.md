# Outreach Timing Optimization Guide

## The Evidence-Based Case for Timing

Most care management outreach fails before the conversation starts.

**Key insight**: Workers without paid sick leave are 3x more likely to skip needed care (DeRigne et al., 2016). If your outreach strategy assumes members can answer phones during business hours, you're systematically failing the working poor.

## The Timing Mismatch Problem

### What Most Programs Do

| Time Block | Outreach Volume | Typical Population |
|------------|-----------------|-------------------|
| 9am - 12pm | 40% | Office workers |
| 12pm - 1pm | 10% | Lunch break |
| 1pm - 5pm | 45% | Office workers |
| After 5pm | 5% | Minimal |

### What the Data Shows

Members with **high no-show rates** and **low contact rates** often share characteristics:
- Hourly wage employment
- Multiple jobs
- Single caregivers
- Retail/service/manufacturing shifts

These members are **not disengaged**. They're unavailable during business hours.

---

## Implementation Framework

### Step 1: Segment by Reachability Pattern

Use claims and demographic data to infer work patterns:

**Indicators of Non-Traditional Schedule:**
- ED visits clustered on evenings/weekends (suggests daytime work)
- Pharmacy fills at 24-hour locations after 6pm
- Appointment no-shows concentrated on weekday daytime
- Occupation codes (if available) indicating shift work

**SQL Proxy for Work Schedule:**
```sql
SELECT
    member_id,
    CASE
        WHEN COUNT(CASE WHEN DATEPART(hour, service_time) >= 18
                        OR DATEPART(weekday, service_date) IN (1, 7)
                   THEN 1 END) > COUNT(*) * 0.4
        THEN 'LIKELY_DAY_SHIFT'
        WHEN COUNT(CASE WHEN DATEPART(hour, service_time) BETWEEN 6 AND 14
                   THEN 1 END) > COUNT(*) * 0.6
        THEN 'LIKELY_EVENING_SHIFT'
        ELSE 'STANDARD_SCHEDULE'
    END AS inferred_schedule
FROM claims
WHERE service_date >= DATEADD(month, -6, GETDATE())
GROUP BY member_id;
```

### Step 2: Match Outreach to Inferred Schedule

| Inferred Schedule | Primary Outreach Window | Backup Window |
|-------------------|-------------------------|---------------|
| Day shift worker | 6:30-7:30pm weekdays | Sat 10am-12pm |
| Evening shift | 10am-12pm weekdays | Sun 2-4pm |
| Night shift | 2-4pm weekdays | Sat 10am-12pm |
| Standard | 10am-12pm, 2-4pm | 6-7pm |
| Unknown | Rotate through all | Track success |

### Step 3: Channel Optimization

Phone is not always the answer.

| Member Characteristic | Preferred Channel | Rationale |
|----------------------|-------------------|-----------|
| Under 35 | SMS first, then phone | Higher text response rates |
| Over 65 | Phone first, then mail | Lower smartphone proficiency |
| Multiple no-shows | SMS appointment link | Removes scheduling friction |
| Non-English primary | Bilingual staff or culturally concordant outreach | Trust and comprehension |
| Rural/low connectivity | Mail with phone follow-up | Reliable delivery |

### Step 4: Callback Scheduling

**Critical insight**: Let members choose when to be called.

Implementation:
1. Initial SMS: "Your health plan wants to help. Reply with best time: A=Morning, B=Afternoon, C=Evening, D=Weekend"
2. Log preference in outreach system
3. Route subsequent calls to preferred window
4. Track success rate by preference

---

## Metrics That Matter

### Stop Measuring
- Total outreach attempts
- "Touches" per member
- Calls made per FTE

### Start Measuring
- Contact rate by time slot
- Engagement rate after contact
- Care gap closure rate
- Time-to-contact for inferred schedule match vs. mismatch

### Sample Dashboard Metrics

```
OUTREACH EFFECTIVENESS DASHBOARD

Segment: Day Shift Workers (n=2,340)

                   Business Hours    Evening Hours    Weekend
Contact Rate            18%              52%            47%
Engagement Rate         34%              61%            58%
Care Gaps Closed        12%              28%            25%
Cost per Closure       $340             $180           $195

RECOMMENDATION: Shift 60% of outreach to evening/weekend for this segment
PROJECTED IMPACT: +16% care gap closure rate, -35% cost per closure
```

---

## Common Objections and Responses

### "Our staff doesn't work evenings/weekends"

Options:
1. Stagger shifts (some staff 11am-7pm instead of 9-5)
2. Partner with vendor that offers extended hours
3. Use automated SMS for initial contact, live staff for follow-up

### "Overtime costs will increase"

Counter: Cost per *successful* outcome matters more than cost per attempt.

If evening outreach doubles your contact rate, you may need half as many attempts per member. Model it:

```
Current: 10 attempts × $8/attempt × 20% contact = $80/contact
Evening: 5 attempts × $12/attempt × 50% contact = $48/contact
Savings: 40% reduction in cost per meaningful contact
```

### "Members don't want to be called after hours"

Reality check:
- Ask them. Use the callback scheduling option.
- Members who prefer evening calls will tell you.
- Members who don't answer during business hours aren't expressing a preference—they're unavailable.

---

## Quick Wins (Week 1-2)

1. **Audit current timing**: What % of your outreach happens after 5pm?
2. **Identify chronic non-contacts**: Pull members with 3+ failed contact attempts
3. **Test evening slot**: Route 20% of chronic non-contacts to 6-7pm window
4. **Track**: Compare contact rate, engagement, and gap closure

## 30-Day Pilot Protocol

**Week 1**: Baseline measurement
- Document current contact rates by time slot
- Identify top 100 chronic non-contacts with high-risk care gaps

**Week 2-3**: Intervention
- Assign 50 members to evening/weekend outreach
- Assign 50 members to standard protocol (control)
- Standardize scripts and channels

**Week 4**: Analysis
- Compare contact rates
- Compare engagement rates
- Compare care gap closure rates
- Calculate cost per closure

**Decision Point**: If evening outreach shows >20% improvement in contact rate with comparable or better engagement, expand to full population segmentation.

---

## References

DeRigne L, Stoddard-Dare P, Quinn L. (2016). Workers Without Paid Sick Leave Less Likely to Take Time Off for Illness or Injury. *Health Affairs*, 35(3), 520-527.

Chaiyachati KH, et al. (2018). Association of Rideshare-Based Transportation Services and Missed Primary Care Appointments. *JAMA Internal Medicine*, 178(3), 383-389.

---

*Part of the Vitals & Variables Edition 18 Toolkit: Care Management AI vs. Member Reality*
