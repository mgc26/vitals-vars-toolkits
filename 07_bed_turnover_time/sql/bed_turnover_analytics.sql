-- Bed Turnover Analytics SQL Queries
-- Comprehensive queries to analyze bed turnover performance
-- Compatible with most major healthcare EMR/ADT systems

-- ============================================
-- 1. CURRENT BED TURNOVER TIME ANALYSIS
-- ============================================
-- Calculate average turnover time by unit with breakdown by phase
WITH bed_turnover_times AS (
    SELECT 
        b.unit_name,
        b.bed_id,
        b.room_number,
        -- Discharge event
        d.discharge_datetime,
        -- EVS notification (first cleaning request after discharge)
        e.evs_notified_datetime,
        -- Cleaning completed
        e.cleaning_completed_datetime,
        -- Next admission
        a.admission_datetime as next_admission,
        
        -- Calculate time segments
        DATEDIFF(minute, d.discharge_datetime, e.evs_notified_datetime) as discharge_to_evs_minutes,
        DATEDIFF(minute, e.evs_notified_datetime, e.cleaning_completed_datetime) as evs_cleaning_minutes,
        DATEDIFF(minute, e.cleaning_completed_datetime, a.admission_datetime) as clean_to_occupied_minutes,
        DATEDIFF(minute, d.discharge_datetime, a.admission_datetime) as total_turnover_minutes
        
    FROM bed_master b
    INNER JOIN discharge_events d ON b.bed_id = d.bed_id
    LEFT JOIN evs_requests e ON b.bed_id = e.bed_id 
        AND e.request_datetime > d.discharge_datetime
        AND e.request_type = 'Discharge Clean'
    LEFT JOIN admission_events a ON b.bed_id = a.bed_id
        AND a.admission_datetime = (
            SELECT MIN(admission_datetime) 
            FROM admission_events 
            WHERE bed_id = b.bed_id 
            AND admission_datetime > d.discharge_datetime
        )
    WHERE 
        d.discharge_datetime >= DATEADD(day, -30, GETDATE())
        AND d.discharge_datetime < GETDATE()
        AND a.admission_datetime IS NOT NULL  -- Only include beds that were refilled
)
SELECT 
    unit_name,
    COUNT(*) as total_turnovers,
    
    -- Average times by phase
    AVG(discharge_to_evs_minutes) as avg_discharge_to_evs,
    AVG(evs_cleaning_minutes) as avg_evs_cleaning,
    AVG(clean_to_occupied_minutes) as avg_clean_to_occupied,
    AVG(total_turnover_minutes) as avg_total_turnover,
    
    -- Percentiles for better insight
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_turnover_minutes) as median_turnover,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY total_turnover_minutes) as p90_turnover,
    
    -- Identify problem areas
    SUM(CASE WHEN total_turnover_minutes > 180 THEN 1 ELSE 0 END) as turnovers_over_3hrs,
    SUM(CASE WHEN total_turnover_minutes > 240 THEN 1 ELSE 0 END) as turnovers_over_4hrs
    
FROM bed_turnover_times
GROUP BY unit_name
ORDER BY avg_total_turnover DESC;

-- ============================================
-- 2. HOURLY DISCHARGE PATTERNS VS EVS STAFFING
-- ============================================
-- Identify mismatches between discharge volume and EVS availability
WITH hourly_patterns AS (
    SELECT 
        DATEPART(hour, discharge_datetime) as discharge_hour,
        DATENAME(weekday, discharge_datetime) as day_of_week,
        COUNT(*) as discharge_count
    FROM discharge_events
    WHERE discharge_datetime >= DATEADD(day, -90, GETDATE())
    GROUP BY 
        DATEPART(hour, discharge_datetime),
        DATENAME(weekday, discharge_datetime)
),
evs_staffing AS (
    SELECT 
        shift_hour,
        day_of_week,
        staff_count
    FROM evs_staffing_schedule
)
SELECT 
    p.discharge_hour,
    p.day_of_week,
    p.discharge_count,
    s.staff_count as evs_staff_available,
    CAST(p.discharge_count AS FLOAT) / NULLIF(s.staff_count, 0) as discharges_per_staff,
    CASE 
        WHEN CAST(p.discharge_count AS FLOAT) / NULLIF(s.staff_count, 0) > 5 THEN 'Understaffed'
        WHEN CAST(p.discharge_count AS FLOAT) / NULLIF(s.staff_count, 0) < 2 THEN 'Overstaffed'
        ELSE 'Balanced'
    END as staffing_assessment
FROM hourly_patterns p
LEFT JOIN evs_staffing s 
    ON p.discharge_hour = s.shift_hour 
    AND p.day_of_week = s.day_of_week
ORDER BY p.day_of_week, p.discharge_hour;

-- ============================================
-- 3. BED TURNOVER BOTTLENECK IDENTIFICATION
-- ============================================
-- Find specific bottlenecks by analyzing incomplete turnovers
SELECT 
    b.unit_name,
    b.bed_id,
    b.room_number,
    d.discharge_datetime,
    e.evs_notified_datetime,
    e.cleaning_completed_datetime,
    
    -- Identify current status
    CASE 
        WHEN d.discharge_datetime IS NOT NULL AND e.evs_notified_datetime IS NULL 
            THEN 'Awaiting EVS Notification'
        WHEN e.evs_notified_datetime IS NOT NULL AND e.cleaning_completed_datetime IS NULL 
            THEN 'EVS Cleaning In Progress'
        WHEN e.cleaning_completed_datetime IS NOT NULL AND b.current_status = 'Clean'
            THEN 'Clean - Awaiting Assignment'
        ELSE 'Other'
    END as bottleneck_status,
    
    -- Time in current status
    CASE 
        WHEN e.evs_notified_datetime IS NULL 
            THEN DATEDIFF(minute, d.discharge_datetime, GETDATE())
        WHEN e.cleaning_completed_datetime IS NULL 
            THEN DATEDIFF(minute, e.evs_notified_datetime, GETDATE())
        WHEN b.current_status = 'Clean'
            THEN DATEDIFF(minute, e.cleaning_completed_datetime, GETDATE())
        ELSE 0
    END as minutes_in_current_status
    
FROM bed_master b
LEFT JOIN discharge_events d ON b.bed_id = d.bed_id
    AND d.discharge_datetime = (
        SELECT MAX(discharge_datetime) 
        FROM discharge_events 
        WHERE bed_id = b.bed_id
    )
LEFT JOIN evs_requests e ON b.bed_id = e.bed_id
    AND e.request_datetime > d.discharge_datetime
    AND e.request_type = 'Discharge Clean'
WHERE 
    b.current_status IN ('Dirty', 'Cleaning', 'Clean')
    AND d.discharge_datetime >= DATEADD(hour, -24, GETDATE())
ORDER BY minutes_in_current_status DESC;

-- ============================================
-- 4. FINANCIAL IMPACT CALCULATION
-- ============================================
-- Calculate revenue loss from extended turnover times
WITH turnover_analysis AS (
    SELECT 
        unit_name,
        COUNT(*) as monthly_turnovers,
        AVG(total_turnover_minutes) as avg_turnover_minutes,
        -- Assume 90 minutes as best practice benchmark
        AVG(total_turnover_minutes) - 90 as excess_minutes,
        -- Convert to hours
        (AVG(total_turnover_minutes) - 90) / 60.0 as excess_hours
    FROM (
        SELECT 
            b.unit_name,
            DATEDIFF(minute, d.discharge_datetime, a.admission_datetime) as total_turnover_minutes
        FROM bed_master b
        INNER JOIN discharge_events d ON b.bed_id = d.bed_id
        INNER JOIN admission_events a ON b.bed_id = a.bed_id
            AND a.admission_datetime = (
                SELECT MIN(admission_datetime) 
                FROM admission_events 
                WHERE bed_id = b.bed_id 
                AND admission_datetime > d.discharge_datetime
            )
        WHERE 
            d.discharge_datetime >= DATEADD(day, -30, GETDATE())
            AND a.admission_datetime IS NOT NULL
    ) t
    GROUP BY unit_name
)
SELECT 
    unit_name,
    monthly_turnovers,
    avg_turnover_minutes,
    excess_minutes,
    
    -- Annual projections
    monthly_turnovers * 12 as annual_turnovers,
    ROUND(monthly_turnovers * 12 * excess_hours, 0) as annual_lost_bed_hours,
    ROUND(monthly_turnovers * 12 * excess_hours / 24, 1) as annual_lost_bed_days,
    
    -- Financial impact (assuming $2000/bed day average)
    ROUND(monthly_turnovers * 12 * excess_hours / 24 * 2000, 0) as annual_revenue_loss
    
FROM turnover_analysis
WHERE excess_minutes > 0
ORDER BY annual_revenue_loss DESC;

-- ============================================
-- 5. PREDICTIVE DISCHARGE PLANNING
-- ============================================
-- Identify patients likely to discharge in next 24 hours
SELECT 
    p.patient_id,
    p.patient_name,
    p.current_bed_id,
    b.unit_name,
    p.admission_datetime,
    DATEDIFF(day, p.admission_datetime, GETDATE()) as current_los,
    p.expected_los,
    p.discharge_planning_status,
    
    -- Discharge readiness indicators
    CASE WHEN med.oral_med_percentage > 80 THEN 1 ELSE 0 END as on_oral_meds,
    CASE WHEN v.stable_vitals_hours > 24 THEN 1 ELSE 0 END as vitals_stable,
    CASE WHEN l.pending_labs = 0 THEN 1 ELSE 0 END as labs_complete,
    CASE WHEN c.pending_consults = 0 THEN 1 ELSE 0 END as consults_complete,
    
    -- Calculate discharge probability score (0-100)
    (
        CASE WHEN DATEDIFF(day, p.admission_datetime, GETDATE()) >= p.expected_los THEN 25 ELSE 0 END +
        CASE WHEN med.oral_med_percentage > 80 THEN 25 ELSE 0 END +
        CASE WHEN v.stable_vitals_hours > 24 THEN 25 ELSE 0 END +
        CASE WHEN l.pending_labs = 0 AND c.pending_consults = 0 THEN 25 ELSE 0 END
    ) as discharge_probability_score
    
FROM patient_census p
INNER JOIN bed_master b ON p.current_bed_id = b.bed_id
LEFT JOIN (
    -- Medication status
    SELECT patient_id, 
           SUM(CASE WHEN route = 'PO' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as oral_med_percentage
    FROM active_medications
    GROUP BY patient_id
) med ON p.patient_id = med.patient_id
LEFT JOIN (
    -- Vital signs stability
    SELECT patient_id,
           DATEDIFF(hour, MAX(abnormal_datetime), GETDATE()) as stable_vitals_hours
    FROM vital_signs
    WHERE abnormal_flag = 1
    GROUP BY patient_id
) v ON p.patient_id = v.patient_id
LEFT JOIN (
    -- Pending labs
    SELECT patient_id, COUNT(*) as pending_labs
    FROM lab_orders
    WHERE status = 'Pending'
    GROUP BY patient_id
) l ON p.patient_id = l.patient_id
LEFT JOIN (
    -- Pending consults
    SELECT patient_id, COUNT(*) as pending_consults
    FROM consult_orders
    WHERE status IN ('Pending', 'In Progress')
    GROUP BY patient_id
) c ON p.patient_id = c.patient_id
WHERE p.discharge_datetime IS NULL
ORDER BY discharge_probability_score DESC, current_los DESC;