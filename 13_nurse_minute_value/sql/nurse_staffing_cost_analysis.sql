/*
==================================================================
Nurse Staffing and Cost Analysis Query
==================================================================

PURPOSE:
Calculate actual RN staffing levels, hours per patient day (HPPD),
and fully-loaded labor costs for cost-per-minute analysis.

INPUTS:
- Nursing payroll data
- Unit census data
- Shift scheduling data

OUTPUTS:
- RN hours per patient day by unit
- Actual vs. budgeted staffing
- Fully-loaded cost per minute by unit
- Total annual nursing labor costs

DATABASE COMPATIBILITY:
- Written for MS SQL Server
- Adaptable for Epic Clarity, Cerner, or other EMR data warehouses
- Adjust table/column names to match your schema

ASSUMPTIONS:
- Benefits multiplier of 1.9x base wage (adjust as needed)
- 730 shifts per FTE per year (2 shifts/day, 365 days)
- 12-hour shifts (adjust for 8-hour or mixed)

USAGE:
Run monthly to track staffing trends and calculate ROI baselines.
==================================================================
*/

-- Set date range for analysis
DECLARE @StartDate DATE = '2024-01-01';
DECLARE @EndDate DATE = '2024-12-31';
DECLARE @BenefitsMultiplier DECIMAL(3,2) = 1.9; -- Adjust based on your org


-- ==================================================================
-- SECTION 1: Calculate RN Hours and Patient Days by Unit
-- ==================================================================

WITH UnitStaffing AS (
    SELECT
        s.unit_id,
        u.unit_name,
        s.shift_date,
        s.shift_type,  -- 'Day', 'Evening', 'Night'
        COUNT(DISTINCT s.nurse_id) AS nurses_on_shift,
        SUM(s.hours_worked) AS total_rn_hours,
        AVG(c.census_count) AS avg_census
    FROM
        nursing_schedule s
    INNER JOIN
        units u ON s.unit_id = u.unit_id
    INNER JOIN
        unit_census c ON s.unit_id = c.unit_id
            AND s.shift_date = c.census_date
    WHERE
        s.shift_date BETWEEN @StartDate AND @EndDate
        AND s.nurse_role = 'RN'  -- Exclude LPNs, CNAs
        AND s.hours_worked > 0   -- Exclude call-offs
    GROUP BY
        s.unit_id, u.unit_name, s.shift_date, s.shift_type
),

-- ==================================================================
-- SECTION 2: Calculate Hours Per Patient Day (HPPD)
-- ==================================================================

UnitHPPD AS (
    SELECT
        unit_id,
        unit_name,
        SUM(total_rn_hours) AS total_rn_hours,
        SUM(avg_census) AS total_patient_days,
        CASE
            WHEN SUM(avg_census) > 0
            THEN SUM(total_rn_hours) / SUM(avg_census)
            ELSE 0
        END AS rn_hppd,
        COUNT(DISTINCT shift_date) AS days_in_period,
        AVG(avg_census) AS avg_daily_census
    FROM
        UnitStaffing
    GROUP BY
        unit_id, unit_name
),

-- ==================================================================
-- SECTION 3: Calculate Actual Wages and Fully-Loaded Costs
-- ==================================================================

NurseWages AS (
    SELECT
        n.nurse_id,
        n.unit_id,
        n.hourly_wage,
        n.hourly_wage * @BenefitsMultiplier AS fully_loaded_hourly,
        (n.hourly_wage * @BenefitsMultiplier) / 60.0 AS cost_per_minute
    FROM
        nurse_payroll n
    WHERE
        n.role = 'RN'
        AND n.is_active = 1
),

UnitCosts AS (
    SELECT
        s.unit_id,
        COUNT(DISTINCT s.nurse_id) AS total_rn_ftes,
        AVG(w.hourly_wage) AS avg_base_wage,
        AVG(w.fully_loaded_hourly) AS avg_fully_loaded_hourly,
        AVG(w.cost_per_minute) AS avg_cost_per_minute
    FROM
        nursing_schedule s
    INNER JOIN
        NurseWages w ON s.nurse_id = w.nurse_id
    WHERE
        s.shift_date BETWEEN @StartDate AND @EndDate
    GROUP BY
        s.unit_id
),

-- ==================================================================
-- SECTION 4: Calculate Annual Labor Costs by Unit
-- ==================================================================

AnnualCosts AS (
    SELECT
        h.unit_id,
        h.unit_name,
        h.total_rn_hours,
        c.avg_fully_loaded_hourly,
        h.total_rn_hours * c.avg_fully_loaded_hourly AS total_annual_labor_cost
    FROM
        UnitHPPD h
    INNER JOIN
        UnitCosts c ON h.unit_id = c.unit_id
)

-- ==================================================================
-- FINAL OUTPUT: Staffing and Cost Metrics
-- ==================================================================

SELECT
    h.unit_name,
    h.total_rn_hours,
    h.total_patient_days,
    ROUND(h.rn_hppd, 2) AS rn_hours_per_patient_day,
    ROUND(h.avg_daily_census, 1) AS avg_daily_census,
    c.total_rn_ftes,

    -- Wage data
    CONCAT('$', FORMAT(c.avg_base_wage, 'N2')) AS avg_base_wage,
    CONCAT('$', FORMAT(c.avg_fully_loaded_hourly, 'N2')) AS avg_fully_loaded_hourly,
    CONCAT('$', FORMAT(c.avg_cost_per_minute, 'N2')) AS cost_per_minute,

    -- Annual cost
    CONCAT('$', FORMAT(a.total_annual_labor_cost, 'N0')) AS total_annual_labor_cost,

    -- Benchmark comparisons
    CASE
        WHEN h.rn_hppd >= 4.5 THEN 'Above Target'
        WHEN h.rn_hppd >= 3.5 THEN 'At Target'
        ELSE 'Below Target'
    END AS hppd_status

FROM
    UnitHPPD h
INNER JOIN
    UnitCosts c ON h.unit_id = c.unit_id
INNER JOIN
    AnnualCosts a ON h.unit_id = a.unit_id
ORDER BY
    h.unit_name;


-- ==================================================================
-- SECTION 5: Summary Statistics (Hospital-Wide)
-- ==================================================================

SELECT
    'Hospital Total' AS metric_name,
    SUM(total_rn_hours) AS total_rn_hours,
    SUM(total_patient_days) AS total_patient_days,
    ROUND(SUM(total_rn_hours) / NULLIF(SUM(total_patient_days), 0), 2) AS overall_rn_hppd,
    SUM(total_rn_ftes) AS total_rn_ftes,
    CONCAT('$', FORMAT(AVG(avg_fully_loaded_hourly), 'N2')) AS avg_fully_loaded_hourly,
    CONCAT('$', FORMAT(SUM(total_annual_labor_cost), 'N0')) AS total_annual_labor_cost
FROM
    UnitHPPD h
INNER JOIN
    UnitCosts c ON h.unit_id = c.unit_id
INNER JOIN
    AnnualCosts a ON h.unit_id = a.unit_id;


-- ==================================================================
-- SECTION 6: Shift-Level Breakdown (for granular analysis)
-- ==================================================================

SELECT
    u.unit_name,
    s.shift_date,
    s.shift_type,
    s.nurses_on_shift,
    ROUND(s.total_rn_hours, 1) AS total_rn_hours,
    ROUND(s.avg_census, 1) AS census,
    CASE
        WHEN s.avg_census > 0
        THEN ROUND(s.total_rn_hours / s.avg_census, 2)
        ELSE 0
    END AS shift_hppd,
    CASE
        WHEN s.avg_census > 0
        THEN ROUND(s.avg_census / s.nurses_on_shift, 1)
        ELSE 0
    END AS patients_per_nurse
FROM
    UnitStaffing s
INNER JOIN
    units u ON s.unit_id = u.unit_id
WHERE
    s.shift_date BETWEEN DATEADD(DAY, -30, GETDATE()) AND GETDATE()  -- Last 30 days
ORDER BY
    u.unit_name, s.shift_date, s.shift_type;


/*
==================================================================
NOTES FOR IMPLEMENTATION:
==================================================================

1. **Table/Column Mapping:**
   - Replace 'nursing_schedule', 'units', 'unit_census', 'nurse_payroll'
     with your actual table names
   - Common table names in Epic Clarity:
     * PAT_ENC_HSP (patient encounters)
     * CLARITY_DEP (departments/units)
     * METRIC_RN_HOURS (if you have a staffing cube)

2. **Benefits Multiplier:**
   - Default is 1.9x (midpoint of 1.8-2.0 range)
   - Validate with your finance team
   - May vary by union contracts, regions, or roles

3. **HPPD Benchmarks:**
   - Medical-Surgical: 4.0-5.5 HPPD
   - ICU: 8.0-12.0 HPPD
   - Step-Down: 5.5-7.5 HPPD
   - ED: Varies widely by acuity/volume
   - Adjust 'hppd_status' thresholds based on your unit types

4. **Use Cases:**
   - Baseline for time-saving interventions ROI
   - Identify understaffed units
   - Budget planning
   - Benchmarking across units

5. **Next Steps:**
   - Save results to a staging table for trend analysis
   - Combine with patient outcome data (mortality, readmissions)
   - Link to time-motion study data

==================================================================
*/
