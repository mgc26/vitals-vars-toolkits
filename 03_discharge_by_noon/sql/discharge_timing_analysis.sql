-- Discharge by Noon Analysis Queries
-- Comprehensive SQL queries for tracking and improving discharge timing
-- Compatible with most major healthcare databases (Epic Clarity, Cerner, etc.)

-- =====================================================
-- 1. BASELINE DISCHARGE TIMING DISTRIBUTION
-- =====================================================
-- Shows hourly distribution of discharges to identify current patterns
WITH discharge_hours AS (
    SELECT 
        EXTRACT(HOUR FROM discharge_time) AS discharge_hour,
        COUNT(*) AS discharge_count,
        COUNT(CASE WHEN EXTRACT(HOUR FROM discharge_time) < 12 THEN 1 END) AS before_noon_count
    FROM 
        patient_encounters
    WHERE 
        discharge_time IS NOT NULL
        AND discharge_time >= DATEADD(day, -30, GETDATE())
        AND encounter_type = 'INPATIENT'
    GROUP BY 
        EXTRACT(HOUR FROM discharge_time)
)
SELECT 
    discharge_hour,
    discharge_count,
    before_noon_count,
    ROUND(100.0 * discharge_count / SUM(discharge_count) OVER(), 2) AS percent_of_total,
    ROUND(100.0 * SUM(before_noon_count) OVER() / SUM(discharge_count) OVER(), 2) AS overall_dbn_rate
FROM 
    discharge_hours
ORDER BY 
    discharge_hour;

-- =====================================================
-- 2. DISCHARGE BY NOON RATES BY UNIT
-- =====================================================
-- Identifies high and low performing units for targeted interventions
SELECT 
    u.unit_name,
    u.unit_type,
    COUNT(pe.encounter_id) AS total_discharges,
    COUNT(CASE WHEN EXTRACT(HOUR FROM pe.discharge_time) < 12 THEN 1 END) AS dbn_count,
    ROUND(100.0 * COUNT(CASE WHEN EXTRACT(HOUR FROM pe.discharge_time) < 12 THEN 1 END) / 
          COUNT(pe.encounter_id), 2) AS dbn_rate,
    AVG(EXTRACT(HOUR FROM pe.discharge_time) + EXTRACT(MINUTE FROM pe.discharge_time)/60.0) AS avg_discharge_hour
FROM 
    patient_encounters pe
    INNER JOIN units u ON pe.unit_id = u.unit_id
WHERE 
    pe.discharge_time IS NOT NULL
    AND pe.discharge_time >= DATEADD(day, -30, GETDATE())
    AND pe.encounter_type = 'INPATIENT'
GROUP BY 
    u.unit_name, u.unit_type
HAVING 
    COUNT(pe.encounter_id) >= 10
ORDER BY 
    dbn_rate DESC;

-- =====================================================
-- 3. WEEKEND VS WEEKDAY DISCHARGE PATTERNS
-- =====================================================
-- Analyzes the "weekend wasteland" effect on discharge timing
SELECT 
    CASE 
        WHEN DATEPART(dw, discharge_date) IN (1, 7) THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    COUNT(*) AS total_discharges,
    COUNT(CASE WHEN EXTRACT(HOUR FROM discharge_time) < 12 THEN 1 END) AS dbn_count,
    ROUND(100.0 * COUNT(CASE WHEN EXTRACT(HOUR FROM discharge_time) < 12 THEN 1 END) / 
          COUNT(*), 2) AS dbn_rate,
    AVG(DATEDIFF(hour, admission_time, discharge_time)) AS avg_los_hours
FROM 
    patient_encounters
WHERE 
    discharge_time IS NOT NULL
    AND discharge_time >= DATEADD(day, -90, GETDATE())
    AND encounter_type = 'INPATIENT'
GROUP BY 
    CASE 
        WHEN DATEPART(dw, discharge_date) IN (1, 7) THEN 'Weekend'
        ELSE 'Weekday'
    END;

-- =====================================================
-- 4. DISCHARGE ORDER TO ACTUAL DISCHARGE TIME LAG
-- =====================================================
-- Identifies process delays between order placement and patient leaving
SELECT 
    u.unit_name,
    AVG(DATEDIFF(minute, do.order_time, pe.discharge_time)) AS avg_lag_minutes,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY DATEDIFF(minute, do.order_time, pe.discharge_time)) AS median_lag_minutes,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY DATEDIFF(minute, do.order_time, pe.discharge_time)) AS p90_lag_minutes,
    COUNT(*) AS discharge_count
FROM 
    patient_encounters pe
    INNER JOIN discharge_orders do ON pe.encounter_id = do.encounter_id
    INNER JOIN units u ON pe.unit_id = u.unit_id
WHERE 
    pe.discharge_time IS NOT NULL
    AND do.order_time IS NOT NULL
    AND pe.discharge_time >= DATEADD(day, -30, GETDATE())
    AND DATEDIFF(minute, do.order_time, pe.discharge_time) BETWEEN 0 AND 720
GROUP BY 
    u.unit_name
HAVING 
    COUNT(*) >= 10
ORDER BY 
    avg_lag_minutes DESC;

-- =====================================================
-- 5. BARRIERS TO DISCHARGE ANALYSIS
-- =====================================================
-- Tracks common reasons for discharge delays
SELECT 
    db.barrier_category,
    db.barrier_description,
    COUNT(*) AS occurrence_count,
    AVG(DATEDIFF(minute, db.identified_time, db.resolved_time)) AS avg_resolution_minutes,
    COUNT(CASE WHEN pe.discharge_time < DATEADD(hour, 12, CAST(pe.discharge_date AS DATE)) THEN 1 END) AS dbn_impact_count
FROM 
    discharge_barriers db
    INNER JOIN patient_encounters pe ON db.encounter_id = pe.encounter_id
WHERE 
    db.identified_time >= DATEADD(day, -30, GETDATE())
    AND pe.encounter_type = 'INPATIENT'
GROUP BY 
    db.barrier_category, db.barrier_description
ORDER BY 
    occurrence_count DESC
LIMIT 20;

-- =====================================================
-- 6. PHYSICIAN ROUNDING TIME IMPACT
-- =====================================================
-- Correlates physician rounding times with discharge success
SELECT 
    p.provider_name,
    p.provider_type,
    AVG(EXTRACT(HOUR FROM pr.round_start_time) + EXTRACT(MINUTE FROM pr.round_start_time)/60.0) AS avg_round_hour,
    COUNT(DISTINCT pr.round_date) AS days_rounded,
    COUNT(pe.encounter_id) AS total_discharges,
    ROUND(100.0 * COUNT(CASE WHEN EXTRACT(HOUR FROM pe.discharge_time) < 12 THEN 1 END) / 
          COUNT(pe.encounter_id), 2) AS dbn_rate
FROM 
    providers p
    INNER JOIN physician_rounds pr ON p.provider_id = pr.provider_id
    INNER JOIN patient_encounters pe ON pr.encounter_id = pe.encounter_id
WHERE 
    pe.discharge_time IS NOT NULL
    AND pr.round_date >= DATEADD(day, -30, GETDATE())
    AND pe.encounter_type = 'INPATIENT'
GROUP BY 
    p.provider_name, p.provider_type
HAVING 
    COUNT(pe.encounter_id) >= 20
ORDER BY 
    dbn_rate DESC;

-- =====================================================
-- 7. NEXT-DAY DISCHARGE PREDICTION CANDIDATES
-- =====================================================
-- Identifies patients likely to discharge tomorrow for proactive planning
SELECT 
    pe.encounter_id,
    pe.patient_name,
    pe.unit_name,
    pe.attending_physician,
    DATEDIFF(day, pe.admission_date, GETDATE()) AS current_los_days,
    pe.expected_discharge_date,
    CASE 
        WHEN lab.pending_critical_results > 0 THEN 'Lab Results Pending'
        WHEN con.active_consults > 0 THEN 'Consults Pending'
        WHEN med.iv_medications > 0 THEN 'IV Medications'
        WHEN pe.discharge_disposition = 'HOME' THEN 'Ready - Home'
        WHEN pe.discharge_disposition IS NOT NULL THEN 'Ready - ' || pe.discharge_disposition
        ELSE 'Needs Assessment'
    END AS discharge_readiness,
    ROUND(
        CASE 
            WHEN DATEDIFF(day, pe.admission_date, GETDATE()) >= pe.expected_los THEN 0.8
            WHEN lab.pending_critical_results = 0 AND con.active_consults = 0 THEN 0.7
            WHEN med.iv_medications = 0 THEN 0.6
            ELSE 0.3
        END, 2
    ) AS discharge_probability
FROM 
    patient_encounters pe
    LEFT JOIN (
        SELECT encounter_id, COUNT(*) AS pending_critical_results
        FROM lab_results
        WHERE result_status = 'PENDING' AND is_critical = 1
        GROUP BY encounter_id
    ) lab ON pe.encounter_id = lab.encounter_id
    LEFT JOIN (
        SELECT encounter_id, COUNT(*) AS active_consults
        FROM consults
        WHERE consult_status IN ('ORDERED', 'PENDING')
        GROUP BY encounter_id
    ) con ON pe.encounter_id = con.encounter_id
    LEFT JOIN (
        SELECT encounter_id, COUNT(*) AS iv_medications
        FROM medication_orders
        WHERE route = 'IV' AND order_status = 'ACTIVE'
        GROUP BY encounter_id
    ) med ON pe.encounter_id = med.encounter_id
WHERE 
    pe.discharge_time IS NULL
    AND pe.encounter_type = 'INPATIENT'
    AND DATEDIFF(day, pe.admission_date, GETDATE()) >= 1
ORDER BY 
    discharge_probability DESC,
    current_los_days DESC;

-- =====================================================
-- 8. DISCHARGE BY NOON TRENDING
-- =====================================================
-- Tracks DBN performance over time to measure improvement
WITH daily_metrics AS (
    SELECT 
        CAST(discharge_time AS DATE) AS discharge_date,
        COUNT(*) AS total_discharges,
        COUNT(CASE WHEN EXTRACT(HOUR FROM discharge_time) < 12 THEN 1 END) AS dbn_count,
        AVG(EXTRACT(HOUR FROM discharge_time) + EXTRACT(MINUTE FROM discharge_time)/60.0) AS avg_discharge_hour
    FROM 
        patient_encounters
    WHERE 
        discharge_time IS NOT NULL
        AND discharge_time >= DATEADD(day, -90, GETDATE())
        AND encounter_type = 'INPATIENT'
    GROUP BY 
        CAST(discharge_time AS DATE)
)
SELECT 
    discharge_date,
    total_discharges,
    dbn_count,
    ROUND(100.0 * dbn_count / total_discharges, 2) AS dbn_rate,
    avg_discharge_hour,
    AVG(ROUND(100.0 * dbn_count / total_discharges, 2)) 
        OVER (ORDER BY discharge_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS seven_day_avg_dbn_rate
FROM 
    daily_metrics
WHERE 
    total_discharges >= 5
ORDER BY 
    discharge_date DESC;

-- =====================================================
-- 9. MEDICATION RECONCILIATION IMPACT
-- =====================================================
-- Analyzes how medication reconciliation affects discharge timing
SELECT 
    CASE 
        WHEN mr.reconciliation_time < DATEADD(hour, 16, DATEADD(day, -1, CAST(pe.discharge_date AS DATE))) 
        THEN 'Previous Day'
        WHEN mr.reconciliation_time < DATEADD(hour, 8, CAST(pe.discharge_date AS DATE)) 
        THEN 'Early Morning'
        WHEN mr.reconciliation_time < DATEADD(hour, 12, CAST(pe.discharge_date AS DATE)) 
        THEN 'Late Morning'
        ELSE 'Afternoon'
    END AS reconciliation_timing,
    COUNT(*) AS discharge_count,
    ROUND(100.0 * COUNT(CASE WHEN EXTRACT(HOUR FROM pe.discharge_time) < 12 THEN 1 END) / 
          COUNT(*), 2) AS dbn_rate,
    AVG(DATEDIFF(minute, mr.reconciliation_time, pe.discharge_time)) AS avg_recon_to_discharge_minutes
FROM 
    patient_encounters pe
    INNER JOIN medication_reconciliation mr ON pe.encounter_id = mr.encounter_id
WHERE 
    pe.discharge_time IS NOT NULL
    AND mr.reconciliation_time IS NOT NULL
    AND pe.discharge_time >= DATEADD(day, -30, GETDATE())
    AND pe.encounter_type = 'INPATIENT'
GROUP BY 
    CASE 
        WHEN mr.reconciliation_time < DATEADD(hour, 16, DATEADD(day, -1, CAST(pe.discharge_date AS DATE))) 
        THEN 'Previous Day'
        WHEN mr.reconciliation_time < DATEADD(hour, 8, CAST(pe.discharge_date AS DATE)) 
        THEN 'Early Morning'
        WHEN mr.reconciliation_time < DATEADD(hour, 12, CAST(pe.discharge_date AS DATE)) 
        THEN 'Late Morning'
        ELSE 'Afternoon'
    END
ORDER BY 
    dbn_rate DESC;

-- =====================================================
-- 10. TRANSPORT AVAILABILITY ANALYSIS
-- =====================================================
-- Identifies transport bottlenecks affecting discharge timing
SELECT 
    EXTRACT(HOUR FROM tr.request_time) AS request_hour,
    COUNT(*) AS transport_requests,
    AVG(DATEDIFF(minute, tr.request_time, tr.pickup_time)) AS avg_wait_minutes,
    COUNT(CASE WHEN tr.transport_type = 'DISCHARGE' THEN 1 END) AS discharge_transports,
    COUNT(CASE WHEN tr.cancelled = 1 THEN 1 END) AS cancelled_count
FROM 
    transport_requests tr
WHERE 
    tr.request_time >= DATEADD(day, -30, GETDATE())
    AND EXTRACT(HOUR FROM tr.request_time) BETWEEN 6 AND 18
GROUP BY 
    EXTRACT(HOUR FROM tr.request_time)
ORDER BY 
    request_hour;