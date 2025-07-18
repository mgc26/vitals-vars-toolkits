-- Discharge Barriers and Intervention Tracking
-- SQL queries to identify and monitor common discharge delays
-- Use these queries to build dashboards and daily reports

-- =====================================================
-- 1. REAL-TIME DISCHARGE READINESS DASHBOARD
-- =====================================================
-- Live view of patients ready for discharge today
CREATE OR REPLACE VIEW v_discharge_ready_today AS
SELECT 
    pe.encounter_id,
    pe.patient_name,
    pe.patient_mrn,
    u.unit_name,
    pe.room_bed,
    pe.attending_physician,
    pe.case_manager,
    DATEDIFF(day, pe.admission_date, GETDATE()) AS los_days,
    
    -- Discharge readiness indicators
    CASE WHEN do.order_time IS NOT NULL THEN 'Yes' ELSE 'No' END AS discharge_ordered,
    CASE WHEN do.order_time IS NOT NULL 
         THEN DATEDIFF(minute, do.order_time, GETDATE()) 
         ELSE NULL END AS minutes_since_order,
    
    -- Clinical readiness
    CASE WHEN vs.stable_vitals = 1 THEN 'Stable' ELSE 'Unstable' END AS vitals_status,
    CASE WHEN lab.critical_pending = 0 THEN 'Complete' ELSE 'Pending' END AS labs_status,
    CASE WHEN med.iv_count = 0 THEN 'PO Only' ELSE 'IV Required' END AS medication_route,
    
    -- Operational readiness
    CASE WHEN mr.completed = 1 THEN 'Complete' ELSE 'Pending' END AS med_rec_status,
    CASE WHEN de.education_complete = 1 THEN 'Complete' ELSE 'Pending' END AS education_status,
    CASE WHEN tr.arranged = 1 THEN 'Arranged' ELSE 'Needed' END AS transport_status,
    pe.discharge_disposition,
    
    -- Scoring
    (CASE WHEN do.order_time IS NOT NULL THEN 3 ELSE 0 END +
     CASE WHEN vs.stable_vitals = 1 THEN 2 ELSE 0 END +
     CASE WHEN lab.critical_pending = 0 THEN 2 ELSE 0 END +
     CASE WHEN med.iv_count = 0 THEN 1 ELSE 0 END +
     CASE WHEN mr.completed = 1 THEN 1 ELSE 0 END +
     CASE WHEN de.education_complete = 1 THEN 1 ELSE 0 END) AS readiness_score
     
FROM patient_encounters pe
INNER JOIN units u ON pe.unit_id = u.unit_id
LEFT JOIN discharge_orders do ON pe.encounter_id = do.encounter_id 
    AND do.order_status = 'ACTIVE'
LEFT JOIN (
    SELECT encounter_id, 
           MAX(CASE WHEN all_vitals_stable = 1 THEN 1 ELSE 0 END) AS stable_vitals
    FROM vitals_summary
    WHERE measurement_time >= DATEADD(hour, -4, GETDATE())
    GROUP BY encounter_id
) vs ON pe.encounter_id = vs.encounter_id
LEFT JOIN (
    SELECT encounter_id, 
           SUM(CASE WHEN result_status = 'PENDING' AND is_critical = 1 THEN 1 ELSE 0 END) AS critical_pending
    FROM lab_results
    GROUP BY encounter_id
) lab ON pe.encounter_id = lab.encounter_id
LEFT JOIN (
    SELECT encounter_id, 
           COUNT(CASE WHEN route = 'IV' AND order_status = 'ACTIVE' THEN 1 END) AS iv_count
    FROM medication_orders
    GROUP BY encounter_id
) med ON pe.encounter_id = med.encounter_id
LEFT JOIN (
    SELECT encounter_id, 
           MAX(CASE WHEN reconciliation_status = 'COMPLETE' THEN 1 ELSE 0 END) AS completed
    FROM medication_reconciliation
    GROUP BY encounter_id
) mr ON pe.encounter_id = mr.encounter_id
LEFT JOIN (
    SELECT encounter_id,
           MAX(CASE WHEN education_status = 'COMPLETE' THEN 1 ELSE 0 END) AS education_complete
    FROM discharge_education
    GROUP BY encounter_id
) de ON pe.encounter_id = de.encounter_id
LEFT JOIN (
    SELECT encounter_id,
           MAX(CASE WHEN transport_arranged = 1 THEN 1 ELSE 0 END) AS arranged
    FROM transport_arrangements
    GROUP BY encounter_id
) tr ON pe.encounter_id = tr.encounter_id
WHERE pe.discharge_time IS NULL
  AND pe.encounter_type = 'INPATIENT'
  AND (do.order_time IS NOT NULL OR 
       DATEDIFF(day, pe.admission_date, GETDATE()) >= pe.expected_los OR
       pe.expected_discharge_date = CAST(GETDATE() AS DATE))
ORDER BY readiness_score DESC, minutes_since_order DESC;

-- =====================================================
-- 2. DISCHARGE BARRIER CATEGORIES
-- =====================================================
-- Categorizes and counts barriers by type for Pareto analysis
WITH barrier_categories AS (
    SELECT 
        encounter_id,
        barrier_time,
        CASE 
            WHEN barrier_reason LIKE '%lab%' OR barrier_reason LIKE '%result%' THEN 'Laboratory'
            WHEN barrier_reason LIKE '%medic%' OR barrier_reason LIKE '%pharm%' THEN 'Medication'
            WHEN barrier_reason LIKE '%transport%' OR barrier_reason LIKE '%ride%' THEN 'Transportation'
            WHEN barrier_reason LIKE '%placement%' OR barrier_reason LIKE '%facility%' THEN 'Placement'
            WHEN barrier_reason LIKE '%insurance%' OR barrier_reason LIKE '%auth%' THEN 'Insurance'
            WHEN barrier_reason LIKE '%equip%' OR barrier_reason LIKE '%DME%' THEN 'Equipment'
            WHEN barrier_reason LIKE '%consult%' OR barrier_reason LIKE '%specialist%' THEN 'Consultation'
            WHEN barrier_reason LIKE '%family%' OR barrier_reason LIKE '%decision%' THEN 'Family/Decision'
            WHEN barrier_reason LIKE '%document%' OR barrier_reason LIKE '%paper%' THEN 'Documentation'
            ELSE 'Other'
        END AS barrier_category,
        barrier_reason,
        resolution_time,
        DATEDIFF(minute, barrier_time, COALESCE(resolution_time, GETDATE())) AS barrier_duration_minutes
    FROM discharge_barriers
    WHERE barrier_time >= DATEADD(day, -30, GETDATE())
)
SELECT 
    barrier_category,
    COUNT(*) AS occurrence_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percent_of_total,
    AVG(barrier_duration_minutes) AS avg_duration_minutes,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY barrier_duration_minutes) AS median_duration_minutes,
    SUM(COUNT(*)) OVER (ORDER BY COUNT(*) DESC) AS cumulative_count,
    ROUND(100.0 * SUM(COUNT(*)) OVER (ORDER BY COUNT(*) DESC) / SUM(COUNT(*)) OVER (), 2) AS cumulative_percent
FROM barrier_categories
GROUP BY barrier_category
ORDER BY occurrence_count DESC;

-- =====================================================
-- 3. MULTIDISCIPLINARY ROUNDS EFFECTIVENESS
-- =====================================================
-- Measures impact of morning rounds on discharge success
WITH rounds_data AS (
    SELECT 
        mr.round_date,
        mr.unit_id,
        u.unit_name,
        mr.round_start_time,
        mr.round_end_time,
        EXTRACT(HOUR FROM mr.round_start_time) AS round_hour,
        COUNT(DISTINCT mr.patient_id) AS patients_discussed,
        COUNT(DISTINCT CASE WHEN pe.discharge_date = mr.round_date THEN pe.encounter_id END) AS same_day_discharges,
        COUNT(DISTINCT CASE WHEN pe.discharge_date = mr.round_date 
                            AND EXTRACT(HOUR FROM pe.discharge_time) < 12 THEN pe.encounter_id END) AS dbn_discharges
    FROM multidisciplinary_rounds mr
    INNER JOIN units u ON mr.unit_id = u.unit_id
    LEFT JOIN patient_encounters pe ON mr.patient_id = pe.patient_id 
        AND pe.discharge_date BETWEEN mr.round_date AND DATEADD(day, 1, mr.round_date)
    WHERE mr.round_date >= DATEADD(day, -30, GETDATE())
    GROUP BY mr.round_date, mr.unit_id, u.unit_name, mr.round_start_time, mr.round_end_time
)
SELECT 
    unit_name,
    CASE 
        WHEN round_hour < 9 THEN 'Early (Before 9 AM)'
        WHEN round_hour < 10 THEN 'Standard (9-10 AM)'
        ELSE 'Late (After 10 AM)'
    END AS round_timing,
    COUNT(*) AS round_count,
    AVG(patients_discussed) AS avg_patients_discussed,
    SUM(same_day_discharges) AS total_same_day_discharges,
    SUM(dbn_discharges) AS total_dbn_discharges,
    ROUND(100.0 * SUM(dbn_discharges) / NULLIF(SUM(same_day_discharges), 0), 2) AS dbn_rate_when_discharged
FROM rounds_data
GROUP BY unit_name, 
    CASE 
        WHEN round_hour < 9 THEN 'Early (Before 9 AM)'
        WHEN round_hour < 10 THEN 'Standard (9-10 AM)'
        ELSE 'Late (After 10 AM)'
    END
ORDER BY unit_name, round_timing;

-- =====================================================
-- 4. DISCHARGE PREDICTION ACCURACY
-- =====================================================
-- Tracks accuracy of discharge predictions to improve planning
SELECT 
    prediction_date,
    COUNT(*) AS total_predictions,
    COUNT(CASE WHEN actual_discharge_date = predicted_discharge_date THEN 1 END) AS accurate_predictions,
    COUNT(CASE WHEN actual_discharge_date < predicted_discharge_date THEN 1 END) AS early_discharges,
    COUNT(CASE WHEN actual_discharge_date > predicted_discharge_date THEN 1 END) AS late_discharges,
    COUNT(CASE WHEN actual_discharge_date IS NULL THEN 1 END) AS still_admitted,
    ROUND(100.0 * COUNT(CASE WHEN actual_discharge_date = predicted_discharge_date THEN 1 END) / 
          NULLIF(COUNT(CASE WHEN actual_discharge_date IS NOT NULL THEN 1 END), 0), 2) AS accuracy_rate
FROM discharge_predictions dp
LEFT JOIN patient_encounters pe ON dp.encounter_id = pe.encounter_id
WHERE prediction_date >= DATEADD(day, -30, GETDATE())
  AND predicted_discharge_date <= GETDATE()
GROUP BY prediction_date
ORDER BY prediction_date DESC;

-- =====================================================
-- 5. WEEKEND DISCHARGE OPPORTUNITIES
-- =====================================================
-- Identifies patients who could discharge on weekends but don't
SELECT 
    pe.encounter_id,
    pe.patient_name,
    pe.unit_name,
    pe.attending_physician,
    DATENAME(weekday, pe.admission_date) AS admission_day,
    DATEDIFF(day, pe.admission_date, pe.discharge_date) AS total_los,
    
    -- Count weekend days during stay
    DATEDIFF(week, pe.admission_date, pe.discharge_date) * 2 +
    CASE WHEN DATEPART(weekday, pe.admission_date) = 1 THEN -1 ELSE 0 END +
    CASE WHEN DATEPART(weekday, pe.discharge_date) = 7 THEN -1 ELSE 0 END AS weekend_days_during_stay,
    
    -- Check if discharged on weekend
    CASE WHEN DATEPART(weekday, pe.discharge_date) IN (1, 7) THEN 'Yes' ELSE 'No' END AS weekend_discharge,
    
    -- Clinical complexity indicators
    complexity_score,
    CASE 
        WHEN complexity_score <= 3 THEN 'Low'
        WHEN complexity_score <= 6 THEN 'Medium'
        ELSE 'High'
    END AS complexity_category
    
FROM patient_encounters pe
WHERE pe.discharge_date >= DATEADD(day, -30, GETDATE())
  AND pe.encounter_type = 'INPATIENT'
  AND DATEDIFF(day, pe.admission_date, pe.discharge_date) >= 3
  AND complexity_score <= 6  -- Focus on low-medium complexity
  AND DATEPART(weekday, pe.discharge_date) NOT IN (1, 7)  -- Did NOT discharge on weekend
ORDER BY weekend_days_during_stay DESC, complexity_score;

-- =====================================================
-- 6. DISCHARGE TIME SLOT OPTIMIZATION
-- =====================================================
-- Analyzes optimal time slots for discharge activities
WITH time_slots AS (
    SELECT 
        CASE 
            WHEN EXTRACT(HOUR FROM activity_time) BETWEEN 6 AND 8 THEN '6-8 AM'
            WHEN EXTRACT(HOUR FROM activity_time) BETWEEN 8 AND 10 THEN '8-10 AM'
            WHEN EXTRACT(HOUR FROM activity_time) BETWEEN 10 AND 12 THEN '10 AM-12 PM'
            WHEN EXTRACT(HOUR FROM activity_time) BETWEEN 12 AND 14 THEN '12-2 PM'
            WHEN EXTRACT(HOUR FROM activity_time) BETWEEN 14 AND 16 THEN '2-4 PM'
            ELSE 'After 4 PM'
        END AS time_slot,
        activity_type,
        encounter_id,
        CASE WHEN completion_time IS NOT NULL THEN 1 ELSE 0 END AS completed,
        DATEDIFF(minute, activity_time, completion_time) AS duration_minutes
    FROM discharge_activities
    WHERE activity_time >= DATEADD(day, -30, GETDATE())
)
SELECT 
    time_slot,
    activity_type,
    COUNT(*) AS activity_count,
    AVG(CASE WHEN completed = 1 THEN duration_minutes END) AS avg_duration_minutes,
    ROUND(100.0 * SUM(completed) / COUNT(*), 2) AS completion_rate
FROM time_slots
WHERE time_slot != 'After 4 PM'
GROUP BY time_slot, activity_type
ORDER BY 
    CASE time_slot
        WHEN '6-8 AM' THEN 1
        WHEN '8-10 AM' THEN 2
        WHEN '10 AM-12 PM' THEN 3
        WHEN '12-2 PM' THEN 4
        WHEN '2-4 PM' THEN 5
    END,
    activity_type;

-- =====================================================
-- 7. PROVIDER DISCHARGE PATTERNS
-- =====================================================
-- Analyzes individual provider performance for coaching
SELECT 
    p.provider_name,
    p.provider_type,
    p.service_line,
    COUNT(DISTINCT pe.encounter_id) AS total_discharges,
    
    -- Timing metrics
    AVG(EXTRACT(HOUR FROM do.order_time) + EXTRACT(MINUTE FROM do.order_time)/60.0) AS avg_order_hour,
    AVG(EXTRACT(HOUR FROM pe.discharge_time) + EXTRACT(MINUTE FROM pe.discharge_time)/60.0) AS avg_discharge_hour,
    
    -- Performance metrics
    ROUND(100.0 * COUNT(CASE WHEN EXTRACT(HOUR FROM pe.discharge_time) < 12 THEN 1 END) / 
          COUNT(pe.encounter_id), 2) AS dbn_rate,
    ROUND(100.0 * COUNT(CASE WHEN EXTRACT(HOUR FROM do.order_time) < 10 THEN 1 END) / 
          COUNT(pe.encounter_id), 2) AS early_order_rate,
    
    -- Process metrics
    AVG(DATEDIFF(minute, do.order_time, pe.discharge_time)) AS avg_order_to_discharge_minutes,
    COUNT(CASE WHEN DATEPART(weekday, pe.discharge_date) IN (1, 7) THEN 1 END) AS weekend_discharges
    
FROM providers p
INNER JOIN patient_encounters pe ON p.provider_id = pe.attending_provider_id
INNER JOIN discharge_orders do ON pe.encounter_id = do.encounter_id
WHERE pe.discharge_date >= DATEADD(day, -30, GETDATE())
  AND pe.encounter_type = 'INPATIENT'
GROUP BY p.provider_name, p.provider_type, p.service_line
HAVING COUNT(DISTINCT pe.encounter_id) >= 10
ORDER BY dbn_rate DESC;

-- =====================================================
-- 8. DISCHARGE PROCESS BOTTLENECK FINDER
-- =====================================================
-- Identifies which steps in discharge process take longest
WITH process_steps AS (
    SELECT 
        ps.encounter_id,
        ps.step_name,
        ps.step_sequence,
        ps.start_time,
        ps.end_time,
        DATEDIFF(minute, ps.start_time, ps.end_time) AS step_duration_minutes,
        ps.responsible_role,
        pe.discharge_time,
        CASE WHEN EXTRACT(HOUR FROM pe.discharge_time) < 12 THEN 1 ELSE 0 END AS dbn_flag
    FROM discharge_process_steps ps
    INNER JOIN patient_encounters pe ON ps.encounter_id = pe.encounter_id
    WHERE ps.start_time >= DATEADD(day, -30, GETDATE())
      AND ps.end_time IS NOT NULL
)
SELECT 
    step_name,
    responsible_role,
    COUNT(*) AS step_count,
    AVG(step_duration_minutes) AS avg_duration_minutes,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY step_duration_minutes) AS median_duration_minutes,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY step_duration_minutes) AS p90_duration_minutes,
    AVG(CASE WHEN dbn_flag = 1 THEN step_duration_minutes END) AS avg_duration_dbn,
    AVG(CASE WHEN dbn_flag = 0 THEN step_duration_minutes END) AS avg_duration_non_dbn,
    ROUND(AVG(CASE WHEN dbn_flag = 0 THEN step_duration_minutes END) - 
          AVG(CASE WHEN dbn_flag = 1 THEN step_duration_minutes END), 2) AS dbn_time_savings
FROM process_steps
GROUP BY step_name, responsible_role
HAVING COUNT(*) >= 20
ORDER BY avg_duration_minutes DESC;

-- =====================================================
-- 9. DISCHARGE COMMUNICATION TRACKING
-- =====================================================
-- Monitors communication patterns affecting discharge timing
SELECT 
    c.communication_type,
    c.sender_role,
    c.recipient_role,
    EXTRACT(HOUR FROM c.sent_time) AS communication_hour,
    COUNT(*) AS message_count,
    AVG(DATEDIFF(minute, c.sent_time, c.read_time)) AS avg_read_delay_minutes,
    AVG(DATEDIFF(minute, c.sent_time, c.response_time)) AS avg_response_delay_minutes,
    COUNT(CASE WHEN c.urgent_flag = 1 THEN 1 END) AS urgent_count,
    COUNT(CASE WHEN pe.discharge_time < DATEADD(hour, 12, CAST(pe.discharge_date AS DATE)) THEN 1 END) AS related_to_dbn
FROM discharge_communications c
INNER JOIN patient_encounters pe ON c.encounter_id = pe.encounter_id
WHERE c.sent_time >= DATEADD(day, -30, GETDATE())
  AND pe.discharge_time IS NOT NULL
GROUP BY c.communication_type, c.sender_role, c.recipient_role, EXTRACT(HOUR FROM c.sent_time)
HAVING COUNT(*) >= 10
ORDER BY communication_hour, avg_response_delay_minutes DESC;

-- =====================================================
-- 10. DISCHARGE BY NOON SCORECARD
-- =====================================================
-- Executive summary view for leadership dashboards
WITH current_month AS (
    SELECT 
        COUNT(*) AS total_discharges,
        COUNT(CASE WHEN EXTRACT(HOUR FROM discharge_time) < 12 THEN 1 END) AS dbn_count,
        AVG(EXTRACT(HOUR FROM discharge_time) + EXTRACT(MINUTE FROM discharge_time)/60.0) AS avg_discharge_hour,
        COUNT(CASE WHEN DATEPART(weekday, discharge_date) IN (1, 7) THEN 1 END) AS weekend_discharges
    FROM patient_encounters
    WHERE discharge_date >= DATEADD(day, -30, GETDATE())
      AND encounter_type = 'INPATIENT'
),
previous_month AS (
    SELECT 
        COUNT(*) AS total_discharges,
        COUNT(CASE WHEN EXTRACT(HOUR FROM discharge_time) < 12 THEN 1 END) AS dbn_count,
        AVG(EXTRACT(HOUR FROM discharge_time) + EXTRACT(MINUTE FROM discharge_time)/60.0) AS avg_discharge_hour
    FROM patient_encounters
    WHERE discharge_date >= DATEADD(day, -60, GETDATE())
      AND discharge_date < DATEADD(day, -30, GETDATE())
      AND encounter_type = 'INPATIENT'
)
SELECT 
    'Current Month' AS period,
    cm.total_discharges,
    cm.dbn_count,
    ROUND(100.0 * cm.dbn_count / cm.total_discharges, 2) AS dbn_rate,
    ROUND(cm.avg_discharge_hour, 2) AS avg_discharge_hour,
    ROUND(100.0 * cm.weekend_discharges / cm.total_discharges, 2) AS weekend_discharge_rate,
    ROUND(100.0 * cm.dbn_count / cm.total_discharges - 
          100.0 * pm.dbn_count / pm.total_discharges, 2) AS dbn_rate_change,
    CASE 
        WHEN cm.dbn_count / cm.total_discharges > pm.dbn_count / pm.total_discharges 
        THEN 'Improving'
        ELSE 'Declining'
    END AS trend
FROM current_month cm, previous_month pm;