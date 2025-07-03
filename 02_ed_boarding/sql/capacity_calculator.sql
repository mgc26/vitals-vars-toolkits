-- Staffing-Adjusted Capacity Calculator
-- Calculates true available capacity considering both physical beds and staffing levels
-- Identifies the real bottleneck (beds vs staff) by unit and shift

WITH bed_capacity AS (
    -- Physical bed availability by unit
    SELECT 
        u.unit_name,
        u.unit_type,
        u.total_beds,
        u.blocked_beds,  -- Beds out of service
        u.total_beds - u.blocked_beds AS physical_beds_available
    FROM unit_configuration u
    WHERE u.is_active = 1
),

staffing_levels AS (
    -- Current and target staffing by unit and shift
    SELECT 
        s.unit_name,
        s.shift_date,
        s.shift_type,  -- 'Day', 'Evening', 'Night'
        s.nurses_scheduled,
        s.nurses_actual,
        s.target_nurse_patient_ratio,
        
        -- Calculate staffed bed capacity based on actual nurses
        FLOOR(s.nurses_actual * s.target_nurse_patient_ratio) AS staffed_bed_capacity
        
    FROM staffing_schedule s
    WHERE s.shift_date >= DATEADD(DAY, -7, GETDATE())  -- Last 7 days
),

current_occupancy AS (
    -- Current patients in each unit
    SELECT 
        unit_name,
        COUNT(*) AS current_census,
        SUM(CASE WHEN expected_discharge_date = CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) AS pending_discharges_today,
        SUM(CASE WHEN admission_datetime > DATEADD(HOUR, -24, GETDATE()) THEN 1 ELSE 0 END) AS admits_last_24h
    FROM current_inpatients
    GROUP BY unit_name
)

-- Combined capacity analysis
SELECT 
    bc.unit_name,
    bc.unit_type,
    bc.total_beds,
    bc.physical_beds_available,
    ISNULL(sl.staffed_bed_capacity, 0) AS current_staffed_capacity,
    ISNULL(co.current_census, 0) AS current_census,
    
    -- True available capacity (minimum of physical and staffed)
    LEAST(bc.physical_beds_available, ISNULL(sl.staffed_bed_capacity, 0)) AS true_available_beds,
    
    -- Identify bottleneck
    CASE 
        WHEN bc.physical_beds_available > ISNULL(sl.staffed_bed_capacity, 0) THEN 'Staffing Limited'
        WHEN bc.physical_beds_available < ISNULL(sl.staffed_bed_capacity, 0) THEN 'Bed Limited'
        ELSE 'Balanced'
    END AS bottleneck_type,
    
    -- Capacity metrics
    CASE 
        WHEN bc.physical_beds_available > 0 
        THEN (bc.physical_beds_available - ISNULL(sl.staffed_bed_capacity, 0)) 
        ELSE 0 
    END AS unstaffed_beds,
    
    ISNULL(co.pending_discharges_today, 0) AS pending_discharges,
    ISNULL(co.admits_last_24h, 0) AS recent_admits,
    
    -- Utilization rates
    CAST(ISNULL(co.current_census, 0) AS FLOAT) / NULLIF(bc.total_beds, 0) * 100 AS physical_occupancy_pct,
    CAST(ISNULL(co.current_census, 0) AS FLOAT) / NULLIF(ISNULL(sl.staffed_bed_capacity, 0), 0) * 100 AS staffed_occupancy_pct

FROM bed_capacity bc
LEFT JOIN (
    -- Get most recent shift data per unit
    SELECT DISTINCT 
        unit_name,
        FIRST_VALUE(staffed_bed_capacity) OVER (PARTITION BY unit_name ORDER BY shift_date DESC, shift_type) AS staffed_bed_capacity
    FROM staffing_levels
) sl ON bc.unit_name = sl.unit_name
LEFT JOIN current_occupancy co ON bc.unit_name = co.unit_name

ORDER BY true_available_beds ASC;  -- Units with least capacity first

-- Shift-based capacity trends
SELECT 
    shift_type,
    AVG(nurses_actual / NULLIF(nurses_scheduled, 0)) * 100 AS avg_staffing_fill_rate,
    AVG(staffed_bed_capacity) AS avg_staffed_beds,
    COUNT(DISTINCT unit_name) AS units_affected,
    SUM(CASE WHEN nurses_actual < nurses_scheduled * 0.8 THEN 1 ELSE 0 END) AS critical_shortage_shifts
FROM staffing_levels
GROUP BY shift_type
ORDER BY avg_staffing_fill_rate ASC;

-- Calculate system-wide capacity gap
SELECT 
    SUM(physical_beds_available) AS total_physical_beds_available,
    SUM(current_staffed_capacity) AS total_staffed_capacity,
    SUM(unstaffed_beds) AS total_unstaffed_beds,
    SUM(unstaffed_beds) * 24 * 365 * 500 AS annual_revenue_loss_from_unstaffed_beds  -- Assuming $500/day revenue
FROM (
    SELECT 
        bc.unit_name,
        bc.physical_beds_available,
        ISNULL(sl.staffed_bed_capacity, 0) AS current_staffed_capacity,
        CASE 
            WHEN bc.physical_beds_available > ISNULL(sl.staffed_bed_capacity, 0) 
            THEN (bc.physical_beds_available - ISNULL(sl.staffed_bed_capacity, 0)) 
            ELSE 0 
        END AS unstaffed_beds
    FROM bed_capacity bc
    LEFT JOIN (
        SELECT DISTINCT 
            unit_name,
            FIRST_VALUE(staffed_bed_capacity) OVER (PARTITION BY unit_name ORDER BY shift_date DESC, shift_type) AS staffed_bed_capacity
        FROM staffing_levels
    ) sl ON bc.unit_name = sl.unit_name
) capacity_summary;