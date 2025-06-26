-- First-Case On-Time Start (FCOTS) SQL Queries
-- Compatible with most SQL databases (adjust date functions as needed)

-- =====================================================
-- 1. BASIC FCOTS CALCULATION
-- =====================================================

-- Daily FCOTS percentage
WITH first_cases AS (
    SELECT 
        DATE(scheduled_start) as surgery_date,
        room_id,
        scheduled_start,
        actual_wheels_in,
        CASE 
            WHEN actual_wheels_in <= scheduled_start THEN 1 
            ELSE 0 
        END as on_time_flag,
        TIMESTAMPDIFF(MINUTE, scheduled_start, actual_wheels_in) as delay_minutes
    FROM 
        or_cases
    WHERE 
        case_sequence = 1  -- First case of the day
        AND DATE(scheduled_start) >= CURRENT_DATE - INTERVAL 30 DAY
)
SELECT 
    surgery_date,
    COUNT(*) as total_first_cases,
    SUM(on_time_flag) as on_time_cases,
    ROUND(100.0 * SUM(on_time_flag) / COUNT(*), 1) as fcots_percent,
    AVG(CASE WHEN delay_minutes > 0 THEN delay_minutes END) as avg_delay_when_late
FROM 
    first_cases
GROUP BY 
    surgery_date
ORDER BY 
    surgery_date DESC;


-- =====================================================
-- 2. DELAY REASON ANALYSIS
-- =====================================================

-- Pareto analysis of delay reasons
WITH delayed_cases AS (
    SELECT 
        c.case_id,
        c.delay_minutes,
        d.delay_reason,
        d.delay_category
    FROM 
        or_cases c
        INNER JOIN or_delays d ON c.case_id = d.case_id
    WHERE 
        c.case_sequence = 1
        AND c.actual_wheels_in > c.scheduled_start
        AND DATE(c.scheduled_start) >= CURRENT_DATE - INTERVAL 90 DAY
)
SELECT 
    delay_category,
    delay_reason,
    COUNT(*) as frequency,
    SUM(delay_minutes) as total_delay_minutes,
    ROUND(AVG(delay_minutes), 1) as avg_delay_minutes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as percent_of_delays,
    SUM(COUNT(*)) OVER (ORDER BY COUNT(*) DESC) as cumulative_count,
    ROUND(100.0 * SUM(COUNT(*)) OVER (ORDER BY COUNT(*) DESC) / SUM(COUNT(*)) OVER (), 1) as cumulative_percent
FROM 
    delayed_cases
GROUP BY 
    delay_category, delay_reason
ORDER BY 
    frequency DESC;


-- =====================================================
-- 3. SURGEON PERFORMANCE SCORECARD
-- =====================================================

-- Individual surgeon FCOTS metrics
WITH surgeon_first_cases AS (
    SELECT 
        s.surgeon_id,
        s.surgeon_name,
        c.case_id,
        CASE 
            WHEN c.actual_wheels_in <= c.scheduled_start THEN 1 
            ELSE 0 
        END as on_time_flag,
        TIMESTAMPDIFF(MINUTE, c.scheduled_start, c.actual_wheels_in) as delay_minutes
    FROM 
        or_cases c
        INNER JOIN surgeons s ON c.surgeon_id = s.surgeon_id
    WHERE 
        c.case_sequence = 1
        AND DATE(c.scheduled_start) >= CURRENT_DATE - INTERVAL 30 DAY
)
SELECT 
    surgeon_id,
    surgeon_name,
    COUNT(*) as total_first_cases,
    SUM(on_time_flag) as on_time_cases,
    ROUND(100.0 * SUM(on_time_flag) / COUNT(*), 1) as fcots_percent,
    AVG(CASE WHEN delay_minutes > 0 THEN delay_minutes END) as avg_delay_when_late,
    SUM(CASE WHEN delay_minutes > 0 THEN delay_minutes ELSE 0 END) as total_delay_minutes,
    CASE 
        WHEN ROUND(100.0 * SUM(on_time_flag) / COUNT(*), 1) >= 90 THEN 'Exceeds Target'
        WHEN ROUND(100.0 * SUM(on_time_flag) / COUNT(*), 1) >= 85 THEN 'Meets Target'
        WHEN ROUND(100.0 * SUM(on_time_flag) / COUNT(*), 1) >= 75 THEN 'Approaching Target'
        ELSE 'Needs Improvement'
    END as performance_tier
FROM 
    surgeon_first_cases
GROUP BY 
    surgeon_id, surgeon_name
HAVING 
    COUNT(*) >= 5  -- Minimum case volume for fair comparison
ORDER BY 
    fcots_percent DESC;


-- =====================================================
-- 4. ROOM UTILIZATION IMPACT
-- =====================================================

-- Calculate lost OR time and financial impact
WITH room_delays AS (
    SELECT 
        room_id,
        DATE(scheduled_start) as surgery_date,
        SUM(CASE 
            WHEN actual_wheels_in > scheduled_start 
            THEN TIMESTAMPDIFF(MINUTE, scheduled_start, actual_wheels_in) 
            ELSE 0 
        END) as daily_delay_minutes
    FROM 
        or_cases
    WHERE 
        case_sequence = 1
        AND DATE(scheduled_start) >= CURRENT_DATE - INTERVAL 30 DAY
    GROUP BY 
        room_id, DATE(scheduled_start)
)
SELECT 
    room_id,
    COUNT(DISTINCT surgery_date) as operating_days,
    SUM(daily_delay_minutes) as total_delay_minutes,
    ROUND(SUM(daily_delay_minutes) / 60.0, 1) as total_delay_hours,
    ROUND(AVG(daily_delay_minutes), 1) as avg_daily_delay_minutes,
    ROUND(SUM(daily_delay_minutes) * 100 / 60.0, 0) as estimated_cost_at_100_per_min
FROM 
    room_delays
GROUP BY 
    room_id
ORDER BY 
    total_delay_minutes DESC;


-- =====================================================
-- 5. TREND ANALYSIS WITH MOVING AVERAGE
-- =====================================================

-- Weekly FCOTS with 4-week moving average
WITH weekly_fcots AS (
    SELECT 
        DATE_TRUNC('week', scheduled_start) as week_start,
        COUNT(*) as total_cases,
        SUM(CASE WHEN actual_wheels_in <= scheduled_start THEN 1 ELSE 0 END) as on_time_cases,
        ROUND(100.0 * SUM(CASE WHEN actual_wheels_in <= scheduled_start THEN 1 ELSE 0 END) / COUNT(*), 1) as fcots_percent
    FROM 
        or_cases
    WHERE 
        case_sequence = 1
        AND DATE(scheduled_start) >= CURRENT_DATE - INTERVAL 180 DAY
    GROUP BY 
        DATE_TRUNC('week', scheduled_start)
)
SELECT 
    week_start,
    fcots_percent,
    ROUND(AVG(fcots_percent) OVER (
        ORDER BY week_start 
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ), 1) as four_week_avg,
    CASE 
        WHEN fcots_percent >= 85 THEN 'Target Met'
        ELSE 'Below Target'
    END as status
FROM 
    weekly_fcots
ORDER BY 
    week_start DESC;


-- =====================================================
-- 6. PRE-OP READINESS DASHBOARD QUERY
-- =====================================================

-- Real-time status for tomorrow's first cases
SELECT 
    c.room_id,
    c.scheduled_start,
    p.patient_name,
    s.surgeon_name,
    a.anesthesiologist_name,
    -- Patient readiness checks
    COALESCE(pc.labs_complete, 0) as labs_complete,
    COALESCE(pc.consent_signed, 0) as consent_signed,
    COALESCE(pc.h_and_p_complete, 0) as h_and_p_complete,
    COALESCE(pc.npo_confirmed, 0) as npo_confirmed,
    -- Equipment readiness
    COALESCE(eq.equipment_ready, 0) as equipment_ready,
    COALESCE(eq.implants_available, 0) as implants_available,
    -- Overall status
    CASE 
        WHEN COALESCE(pc.labs_complete, 0) = 1 
            AND COALESCE(pc.consent_signed, 0) = 1
            AND COALESCE(pc.h_and_p_complete, 0) = 1
            AND COALESCE(pc.npo_confirmed, 0) = 1
            AND COALESCE(eq.equipment_ready, 0) = 1
            AND COALESCE(eq.implants_available, 0) = 1
        THEN 'GREEN - Ready'
        WHEN COALESCE(pc.labs_complete, 0) = 0 
            OR COALESCE(pc.consent_signed, 0) = 0
            OR COALESCE(pc.h_and_p_complete, 0) = 0
        THEN 'RED - Critical Items Missing'
        ELSE 'YELLOW - Minor Items Pending'
    END as overall_status
FROM 
    or_cases c
    INNER JOIN patients p ON c.patient_id = p.patient_id
    INNER JOIN surgeons s ON c.surgeon_id = s.surgeon_id
    INNER JOIN anesthesiologists a ON c.anesthesiologist_id = a.anesthesiologist_id
    LEFT JOIN patient_checklist pc ON c.case_id = pc.case_id
    LEFT JOIN equipment_checklist eq ON c.case_id = eq.case_id
WHERE 
    c.case_sequence = 1
    AND DATE(c.scheduled_start) = CURRENT_DATE + INTERVAL 1 DAY
ORDER BY 
    c.room_id;


-- =====================================================
-- 7. FINANCIAL ROI CALCULATOR
-- =====================================================

-- Calculate potential savings from FCOTS improvement
WITH current_state AS (
    SELECT 
        COUNT(*) as total_first_cases,
        SUM(CASE WHEN actual_wheels_in <= scheduled_start THEN 1 ELSE 0 END) as on_time_cases,
        SUM(CASE 
            WHEN actual_wheels_in > scheduled_start 
            THEN TIMESTAMPDIFF(MINUTE, scheduled_start, actual_wheels_in) 
            ELSE 0 
        END) as total_delay_minutes
    FROM 
        or_cases
    WHERE 
        case_sequence = 1
        AND DATE(scheduled_start) >= CURRENT_DATE - INTERVAL 365 DAY
),
calculations AS (
    SELECT 
        total_first_cases,
        on_time_cases,
        total_delay_minutes,
        ROUND(100.0 * on_time_cases / total_first_cases, 1) as current_fcots,
        total_delay_minutes / 60.0 as total_delay_hours,
        total_delay_minutes * 100 as annual_cost_at_100_per_min
    FROM 
        current_state
)
SELECT 
    current_fcots as current_fcots_percent,
    total_delay_hours as annual_delay_hours,
    annual_cost_at_100_per_min as annual_delay_cost,
    -- Improvement scenarios
    ROUND((85 - current_fcots) * total_delay_hours / (100 - current_fcots), 0) as hours_saved_at_85_percent,
    ROUND((85 - current_fcots) * annual_cost_at_100_per_min / (100 - current_fcots), 0) as savings_at_85_percent,
    ROUND((90 - current_fcots) * total_delay_hours / (100 - current_fcots), 0) as hours_saved_at_90_percent,
    ROUND((90 - current_fcots) * annual_cost_at_100_per_min / (100 - current_fcots), 0) as savings_at_90_percent
FROM 
    calculations;


-- =====================================================
-- NOTES ON CUSTOMIZATION
-- =====================================================
/*
1. Date Functions: 
   - PostgreSQL: DATE_TRUNC, INTERVAL syntax as shown
   - MySQL: DATE_FORMAT, DATE_SUB
   - SQL Server: DATEPART, DATEADD
   - Oracle: TRUNC, ADD_MONTHS

2. Table/Column Names:
   - Adjust to match your EMR schema
   - Common variations: surgery_schedule, or_schedule, case_times

3. Performance Tips:
   - Index on scheduled_start, case_sequence
   - Partition large tables by date
   - Consider materialized views for dashboards

4. Additional Metrics to Consider:
   - Service line specific FCOTS
   - Day of week patterns
   - Seasonal variations
   - Correlation with overtime costs
*/