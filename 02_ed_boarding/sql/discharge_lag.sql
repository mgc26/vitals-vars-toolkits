-- Discharge Lag Analyzer
-- Measures the gap between discharge order and actual patient departure
-- Identifies bottlenecks in the discharge process by unit and time of day

WITH discharge_times AS (
    SELECT 
        a.encounter_id,
        a.patient_id,
        a.unit_name,
        a.admission_datetime,
        a.discharge_order_datetime,
        a.actual_discharge_datetime,
        
        -- Calculate lag in hours
        DATEDIFF(MINUTE, a.discharge_order_datetime, a.actual_discharge_datetime) / 60.0 AS discharge_lag_hours,
        
        -- Time categories
        DATEPART(HOUR, a.discharge_order_datetime) AS order_hour,
        DATEPART(HOUR, a.actual_discharge_datetime) AS discharge_hour,
        DATEPART(WEEKDAY, a.discharge_order_datetime) AS day_of_week,
        
        -- Identify if discharge order was before noon
        CASE 
            WHEN DATEPART(HOUR, a.discharge_order_datetime) < 12 THEN 1 
            ELSE 0 
        END AS order_before_noon,
        
        -- Identify if actual discharge was before noon
        CASE 
            WHEN DATEPART(HOUR, a.actual_discharge_datetime) < 12 THEN 1 
            ELSE 0 
        END AS discharged_before_noon
        
    FROM admissions a
    WHERE 
        a.discharge_order_datetime IS NOT NULL
        AND a.actual_discharge_datetime IS NOT NULL
        AND a.actual_discharge_datetime > a.discharge_order_datetime
        AND a.admission_datetime >= DATEADD(DAY, -90, GETDATE())  -- Last 90 days
)

-- Overall discharge lag statistics
SELECT 
    'Overall' AS analysis_type,
    NULL AS unit_name,
    COUNT(*) AS total_discharges,
    AVG(discharge_lag_hours) AS avg_lag_hours,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY discharge_lag_hours) AS median_lag_hours,
    MAX(discharge_lag_hours) AS max_lag_hours,
    
    -- Morning discharge performance
    SUM(order_before_noon) AS orders_before_noon,
    SUM(discharged_before_noon) AS discharged_before_noon,
    CAST(SUM(discharged_before_noon) AS FLOAT) / NULLIF(SUM(order_before_noon), 0) * 100 AS pct_noon_orders_completed_by_noon,
    
    -- Cost impact (unnecessary bed hours)
    SUM(discharge_lag_hours) AS total_excess_bed_hours,
    SUM(discharge_lag_hours) * 137 AS opportunity_cost  -- Using ED boarding cost
    
FROM discharge_times

UNION ALL

-- Breakdown by unit
SELECT 
    'By Unit' AS analysis_type,
    unit_name,
    COUNT(*) AS total_discharges,
    AVG(discharge_lag_hours) AS avg_lag_hours,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY discharge_lag_hours) AS median_lag_hours,
    MAX(discharge_lag_hours) AS max_lag_hours,
    SUM(order_before_noon) AS orders_before_noon,
    SUM(discharged_before_noon) AS discharged_before_noon,
    CAST(SUM(discharged_before_noon) AS FLOAT) / NULLIF(SUM(order_before_noon), 0) * 100 AS pct_noon_orders_completed_by_noon,
    SUM(discharge_lag_hours) AS total_excess_bed_hours,
    SUM(discharge_lag_hours) * 137 AS opportunity_cost
FROM discharge_times
GROUP BY unit_name

ORDER BY analysis_type, avg_lag_hours DESC;

-- Hourly pattern analysis
SELECT 
    order_hour,
    COUNT(*) AS discharge_orders_written,
    AVG(discharge_lag_hours) AS avg_lag_from_this_hour,
    SUM(CASE WHEN discharge_hour < 12 THEN 1 ELSE 0 END) AS completed_by_noon,
    SUM(CASE WHEN discharge_hour < 14 THEN 1 ELSE 0 END) AS completed_by_2pm,
    SUM(CASE WHEN discharge_hour < 16 THEN 1 ELSE 0 END) AS completed_by_4pm
FROM discharge_times
WHERE order_hour < 12  -- Focus on morning orders
GROUP BY order_hour
ORDER BY order_hour;

-- Identify units with longest discharge delays for targeted intervention
SELECT TOP 5
    unit_name,
    AVG(discharge_lag_hours) AS avg_lag_hours,
    COUNT(*) AS discharge_count,
    SUM(CASE WHEN discharge_lag_hours > 5 THEN 1 ELSE 0 END) AS delays_over_5_hours,
    MAX(discharge_lag_hours) AS worst_delay
FROM discharge_times
GROUP BY unit_name
HAVING COUNT(*) >= 10  -- Minimum volume for significance
ORDER BY avg_lag_hours DESC;