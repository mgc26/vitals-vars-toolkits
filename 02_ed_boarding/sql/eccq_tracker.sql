-- ECCQ (Equity of Emergency Care Capacity and Quality) Compliance Tracker
-- Tracks CMS proposed quality measures for ED boarding and throughput
-- Helps hospitals prepare for upcoming regulatory requirements

WITH ed_metrics AS (
    SELECT 
        e.encounter_id,
        e.patient_id,
        e.ed_arrival_datetime,
        e.triage_datetime,
        e.bed_placement_datetime,
        e.admission_decision_datetime,
        e.ed_departure_datetime,
        e.disposition,
        e.left_without_being_seen,
        e.left_before_medical_screening,
        p.race_ethnicity,
        p.primary_language,
        p.insurance_type,
        
        -- Calculate key time intervals
        DATEDIFF(MINUTE, e.ed_arrival_datetime, e.triage_datetime) / 60.0 AS arrival_to_triage_hours,
        DATEDIFF(MINUTE, e.ed_arrival_datetime, e.bed_placement_datetime) / 60.0 AS wait_for_bed_hours,
        DATEDIFF(MINUTE, e.admission_decision_datetime, e.ed_departure_datetime) / 60.0 AS boarding_hours,
        DATEDIFF(MINUTE, e.ed_arrival_datetime, e.ed_departure_datetime) / 60.0 AS total_ed_hours
        
    FROM ed_encounters e
    INNER JOIN patients p ON e.patient_id = p.patient_id
    WHERE e.ed_arrival_datetime >= DATEADD(MONTH, -3, GETDATE())  -- Last 3 months
)

-- ECCQ Component Metrics
SELECT 
    'ECCQ Compliance Summary' AS report_section,
    COUNT(*) AS total_ed_visits,
    
    -- Component 1: Boarding >4 hours after admission decision
    SUM(CASE WHEN disposition = 'Admitted' AND boarding_hours > 4 THEN 1 ELSE 0 END) AS boarding_over_4h_count,
    CAST(SUM(CASE WHEN disposition = 'Admitted' AND boarding_hours > 4 THEN 1 ELSE 0 END) AS FLOAT) / 
        NULLIF(SUM(CASE WHEN disposition = 'Admitted' THEN 1 ELSE 0 END), 0) * 100 AS boarding_over_4h_pct,
    
    -- Component 2: Total ED stay >8 hours
    SUM(CASE WHEN total_ed_hours > 8 THEN 1 ELSE 0 END) AS total_stay_over_8h_count,
    CAST(SUM(CASE WHEN total_ed_hours > 8 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 AS total_stay_over_8h_pct,
    
    -- Component 3: Wait >1 hour for treatment space
    SUM(CASE WHEN wait_for_bed_hours > 1 THEN 1 ELSE 0 END) AS wait_over_1h_count,
    CAST(SUM(CASE WHEN wait_for_bed_hours > 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 AS wait_over_1h_pct,
    
    -- Component 4: Left without medical screening exam
    SUM(CASE WHEN left_before_medical_screening = 1 THEN 1 ELSE 0 END) AS left_before_screening_count,
    CAST(SUM(CASE WHEN left_before_medical_screening = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 AS left_before_screening_pct,
    
    -- Composite failure rate (any component)
    SUM(CASE 
        WHEN (disposition = 'Admitted' AND boarding_hours > 4)
            OR total_ed_hours > 8
            OR wait_for_bed_hours > 1
            OR left_before_medical_screening = 1
        THEN 1 ELSE 0 
    END) AS any_eccq_failure_count,
    
    CAST(SUM(CASE 
        WHEN (disposition = 'Admitted' AND boarding_hours > 4)
            OR total_ed_hours > 8
            OR wait_for_bed_hours > 1
            OR left_before_medical_screening = 1
        THEN 1 ELSE 0 
    END) AS FLOAT) / COUNT(*) * 100 AS eccq_failure_rate

FROM ed_metrics;

-- Equity analysis by demographics
SELECT 
    'Equity Analysis' AS analysis_type,
    race_ethnicity,
    COUNT(*) AS visits,
    
    -- Boarding disparities
    AVG(CASE WHEN disposition = 'Admitted' THEN boarding_hours END) AS avg_boarding_hours,
    CAST(SUM(CASE WHEN disposition = 'Admitted' AND boarding_hours > 4 THEN 1 ELSE 0 END) AS FLOAT) / 
        NULLIF(SUM(CASE WHEN disposition = 'Admitted' THEN 1 ELSE 0 END), 0) * 100 AS boarding_over_4h_pct,
    
    -- Total time disparities
    AVG(total_ed_hours) AS avg_total_ed_hours,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY total_ed_hours) AS p90_total_ed_hours,
    
    -- LWBS disparities
    CAST(SUM(CASE WHEN left_without_being_seen = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 AS lwbs_rate

FROM ed_metrics
GROUP BY race_ethnicity
HAVING COUNT(*) >= 30  -- Minimum sample size
ORDER BY avg_boarding_hours DESC;

-- Trending by month
SELECT 
    YEAR(ed_arrival_datetime) AS year,
    MONTH(ed_arrival_datetime) AS month,
    COUNT(*) AS total_visits,
    
    -- Trend each ECCQ component
    CAST(SUM(CASE WHEN disposition = 'Admitted' AND boarding_hours > 4 THEN 1 ELSE 0 END) AS FLOAT) / 
        NULLIF(SUM(CASE WHEN disposition = 'Admitted' THEN 1 ELSE 0 END), 0) * 100 AS boarding_over_4h_pct,
    CAST(SUM(CASE WHEN total_ed_hours > 8 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 AS total_over_8h_pct,
    CAST(SUM(CASE WHEN wait_for_bed_hours > 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 AS wait_over_1h_pct,
    CAST(SUM(CASE WHEN left_before_medical_screening = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 AS left_before_screening_pct

FROM ed_metrics
GROUP BY YEAR(ed_arrival_datetime), MONTH(ed_arrival_datetime)
ORDER BY year, month;

-- Worst performing times for targeted intervention
SELECT 
    DATEPART(WEEKDAY, ed_arrival_datetime) AS day_of_week,
    DATEPART(HOUR, ed_arrival_datetime) AS hour_of_day,
    COUNT(*) AS visits,
    CAST(SUM(CASE 
        WHEN (disposition = 'Admitted' AND boarding_hours > 4)
            OR total_ed_hours > 8
            OR wait_for_bed_hours > 1
        THEN 1 ELSE 0 
    END) AS FLOAT) / COUNT(*) * 100 AS eccq_failure_rate

FROM ed_metrics
GROUP BY DATEPART(WEEKDAY, ed_arrival_datetime), DATEPART(HOUR, ed_arrival_datetime)
HAVING COUNT(*) >= 20
ORDER BY eccq_failure_rate DESC
LIMIT 10;