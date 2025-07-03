-- ED Boarding Duration Calculator with Behavioral Health Flags
-- Calculates boarding time for admitted patients waiting for inpatient beds
-- Includes behavioral health identification for specialized tracking

WITH ed_boarding AS (
    SELECT 
        e.encounter_id,
        e.patient_id,
        e.ed_arrival_datetime,
        e.admission_decision_datetime,
        e.ed_departure_datetime,
        e.chief_complaint,
        e.diagnosis_codes,
        
        -- Calculate boarding duration in hours
        DATEDIFF(MINUTE, e.admission_decision_datetime, e.ed_departure_datetime) / 60.0 AS boarding_hours,
        
        -- Identify behavioral health patients
        CASE 
            WHEN e.chief_complaint LIKE '%psych%' 
                OR e.chief_complaint LIKE '%mental%'
                OR e.chief_complaint LIKE '%suicide%'
                OR e.chief_complaint LIKE '%behavioral%'
                OR e.diagnosis_codes LIKE 'F%'  -- ICD-10 mental health codes
            THEN 1 
            ELSE 0 
        END AS is_behavioral_health,
        
        -- Day of week and hour for pattern analysis
        DATEPART(WEEKDAY, e.admission_decision_datetime) AS day_of_week,
        DATEPART(HOUR, e.admission_decision_datetime) AS hour_of_day,
        
        -- Age category
        CASE 
            WHEN p.age >= 65 THEN 'Elderly (65+)'
            WHEN p.age >= 18 THEN 'Adult (18-64)'
            ELSE 'Pediatric (<18)'
        END AS age_category
        
    FROM ed_encounters e
    INNER JOIN patients p ON e.patient_id = p.patient_id
    WHERE 
        e.disposition = 'Admitted'
        AND e.admission_decision_datetime IS NOT NULL
        AND e.ed_departure_datetime > e.admission_decision_datetime
        AND e.ed_arrival_datetime >= DATEADD(DAY, -90, GETDATE())  -- Last 90 days
)

SELECT 
    -- Summary statistics
    COUNT(*) AS total_boarded_patients,
    AVG(boarding_hours) AS avg_boarding_hours,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY boarding_hours) AS median_boarding_hours,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY boarding_hours) AS p90_boarding_hours,
    MAX(boarding_hours) AS max_boarding_hours,
    
    -- Behavioral health breakdown
    SUM(is_behavioral_health) AS behavioral_health_patients,
    AVG(CASE WHEN is_behavioral_health = 1 THEN boarding_hours END) AS avg_behavioral_boarding_hours,
    
    -- ECCQ compliance (>4 hours)
    SUM(CASE WHEN boarding_hours > 4 THEN 1 ELSE 0 END) AS patients_boarding_over_4_hours,
    CAST(SUM(CASE WHEN boarding_hours > 4 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 AS pct_over_4_hours,
    
    -- Cost impact (using $219/hour)
    SUM(boarding_hours) * 219 AS total_boarding_cost,
    
    -- Peak times
    (SELECT TOP 1 day_of_week FROM ed_boarding GROUP BY day_of_week ORDER BY AVG(boarding_hours) DESC) AS worst_day_of_week,
    (SELECT TOP 1 hour_of_day FROM ed_boarding GROUP BY hour_of_day ORDER BY COUNT(*) DESC) AS busiest_hour

FROM ed_boarding;

-- Detailed breakdown by day and hour for heatmap visualization
SELECT 
    day_of_week,
    hour_of_day,
    COUNT(*) AS patient_count,
    AVG(boarding_hours) AS avg_boarding_hours,
    SUM(boarding_hours) AS total_boarding_hours
FROM ed_boarding
GROUP BY day_of_week, hour_of_day
ORDER BY day_of_week, hour_of_day;