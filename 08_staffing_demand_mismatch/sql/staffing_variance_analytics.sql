-- ============================================================================
-- STAFFING VARIANCE ANALYTICS SQL QUERIES
-- ============================================================================
-- Purpose: Comprehensive SQL queries for analyzing staffing variance patterns
-- Compatible with: PostgreSQL, MySQL, SQL Server (with minor adjustments)
-- ============================================================================

-- ============================================================================
-- 1. DAILY STAFFING VARIANCE CALCULATION
-- ============================================================================
-- Calculates variance between scheduled, actual, and required staffing

WITH daily_variance AS (
    SELECT 
        date,
        unit_id,
        unit_name,
        shift,
        census,
        scheduled_staff,
        actual_staff,
        -- Calculate required staff based on nurse-to-patient ratios
        CASE 
            WHEN unit_type = 'ICU' THEN CEIL(census / 2.0)
            WHEN unit_type = 'ED' THEN CEIL(census / 3.0)
            WHEN unit_type = 'Med-Surg' THEN CEIL(census / 4.0)
            WHEN unit_type = 'Telemetry' THEN CEIL(census / 3.5)
            ELSE CEIL(census / 4.0)
        END AS required_staff,
        
        -- Variance calculations
        actual_staff - scheduled_staff AS schedule_variance,
        actual_staff - CEIL(census / 4.0) AS demand_variance,
        
        -- Percentage variance
        ROUND(100.0 * (actual_staff - scheduled_staff) / NULLIF(scheduled_staff, 0), 1) AS schedule_variance_pct,
        ROUND(100.0 * (actual_staff - CEIL(census / 4.0)) / NULLIF(CEIL(census / 4.0), 0), 1) AS demand_variance_pct,
        
        -- Staffing adequacy flags
        CASE 
            WHEN actual_staff < CEIL(census / 4.0) THEN 'Understaffed'
            WHEN actual_staff > CEIL(census / 4.0) * 1.1 THEN 'Overstaffed'
            ELSE 'Adequate'
        END AS staffing_status,
        
        overtime_hours,
        agency_hours,
        sick_calls,
        call_offs
        
    FROM staffing_daily
    WHERE date >= CURRENT_DATE - INTERVAL '90 days'
)
SELECT 
    date,
    unit_name,
    shift,
    census,
    scheduled_staff,
    actual_staff,
    required_staff,
    demand_variance_pct,
    staffing_status,
    overtime_hours,
    agency_hours
FROM daily_variance
ORDER BY date DESC, unit_name, shift;

-- ============================================================================
-- 2. PATTERN ANALYSIS BY DAY OF WEEK
-- ============================================================================
-- Identifies staffing patterns and variance by day of week

WITH dow_patterns AS (
    SELECT 
        EXTRACT(DOW FROM date) AS day_of_week,
        TO_CHAR(date, 'Day') AS day_name,
        unit_id,
        unit_name,
        shift,
        
        -- Average metrics by day of week
        AVG(census) AS avg_census,
        AVG(scheduled_staff) AS avg_scheduled,
        AVG(actual_staff) AS avg_actual,
        AVG(CEIL(census / 4.0)) AS avg_required,
        
        -- Variance metrics
        AVG(actual_staff - CEIL(census / 4.0)) AS avg_variance,
        STDDEV(actual_staff - CEIL(census / 4.0)) AS variance_stddev,
        
        -- Premium labor usage
        SUM(overtime_hours) AS total_overtime,
        SUM(agency_hours) AS total_agency,
        AVG(overtime_hours) AS avg_overtime,
        AVG(agency_hours) AS avg_agency,
        
        -- Frequency metrics
        COUNT(*) AS days_counted,
        SUM(CASE WHEN actual_staff < CEIL(census / 4.0) THEN 1 ELSE 0 END) AS understaffed_days,
        SUM(CASE WHEN overtime_hours > 0 THEN 1 ELSE 0 END) AS overtime_days,
        SUM(CASE WHEN agency_hours > 0 THEN 1 ELSE 0 END) AS agency_days
        
    FROM staffing_daily
    WHERE date >= CURRENT_DATE - INTERVAL '6 months'
    GROUP BY EXTRACT(DOW FROM date), TO_CHAR(date, 'Day'), unit_id, unit_name, shift
)
SELECT 
    day_name,
    unit_name,
    shift,
    ROUND(avg_census, 1) AS avg_census,
    ROUND(avg_scheduled, 1) AS avg_scheduled_staff,
    ROUND(avg_required, 1) AS avg_required_staff,
    ROUND(avg_variance, 1) AS avg_staff_variance,
    ROUND(100.0 * understaffed_days / days_counted, 1) AS pct_days_understaffed,
    ROUND(avg_overtime, 1) AS avg_overtime_hours,
    ROUND(avg_agency, 1) AS avg_agency_hours
FROM dow_patterns
ORDER BY 
    CASE day_of_week 
        WHEN 1 THEN 7  -- Sunday last
        ELSE day_of_week - 1 
    END,
    unit_name,
    shift;

-- ============================================================================
-- 3. MONDAY SURGE ANALYSIS
-- ============================================================================
-- Specifically analyzes Monday patterns vs other weekdays

WITH monday_analysis AS (
    SELECT 
        unit_id,
        unit_name,
        
        -- Monday metrics
        AVG(CASE WHEN EXTRACT(DOW FROM date) = 1 THEN census END) AS monday_avg_census,
        AVG(CASE WHEN EXTRACT(DOW FROM date) = 1 THEN actual_staff END) AS monday_avg_staff,
        AVG(CASE WHEN EXTRACT(DOW FROM date) = 1 THEN overtime_hours END) AS monday_avg_overtime,
        
        -- Other weekday metrics (Tue-Fri)
        AVG(CASE WHEN EXTRACT(DOW FROM date) BETWEEN 2 AND 5 THEN census END) AS other_weekday_avg_census,
        AVG(CASE WHEN EXTRACT(DOW FROM date) BETWEEN 2 AND 5 THEN actual_staff END) AS other_weekday_avg_staff,
        AVG(CASE WHEN EXTRACT(DOW FROM date) BETWEEN 2 AND 5 THEN overtime_hours END) AS other_weekday_avg_overtime,
        
        -- Weekend metrics
        AVG(CASE WHEN EXTRACT(DOW FROM date) IN (0, 6) THEN census END) AS weekend_avg_census,
        AVG(CASE WHEN EXTRACT(DOW FROM date) IN (0, 6) THEN actual_staff END) AS weekend_avg_staff
        
    FROM staffing_daily
    WHERE date >= CURRENT_DATE - INTERVAL '3 months'
        AND shift = 'Day'  -- Focus on day shift for clearest pattern
    GROUP BY unit_id, unit_name
)
SELECT 
    unit_name,
    ROUND(monday_avg_census, 1) AS monday_census,
    ROUND(other_weekday_avg_census, 1) AS other_weekday_census,
    ROUND(100.0 * (monday_avg_census - other_weekday_avg_census) / NULLIF(other_weekday_avg_census, 0), 1) AS monday_surge_pct,
    ROUND(monday_avg_overtime, 1) AS monday_overtime_hrs,
    ROUND(other_weekday_avg_overtime, 1) AS other_weekday_overtime_hrs,
    ROUND(monday_avg_overtime - other_weekday_avg_overtime, 1) AS excess_monday_overtime
FROM monday_analysis
WHERE monday_avg_census IS NOT NULL
ORDER BY monday_surge_pct DESC;

-- ============================================================================
-- 4. OVERTIME AND AGENCY USAGE PATTERNS
-- ============================================================================
-- Analyzes when and why premium labor is used

WITH premium_labor AS (
    SELECT 
        date,
        EXTRACT(HOUR FROM overtime_start_time) AS overtime_hour,
        unit_id,
        unit_name,
        shift,
        
        -- Categorize time of overtime decision
        CASE 
            WHEN EXTRACT(HOUR FROM overtime_start_time) BETWEEN 6 AND 10 THEN 'Morning'
            WHEN EXTRACT(HOUR FROM overtime_start_time) BETWEEN 11 AND 14 THEN 'Midday'
            WHEN EXTRACT(HOUR FROM overtime_start_time) BETWEEN 15 AND 18 THEN 'Afternoon Crisis'
            WHEN EXTRACT(HOUR FROM overtime_start_time) BETWEEN 19 AND 22 THEN 'Evening'
            ELSE 'Night'
        END AS decision_period,
        
        overtime_hours,
        agency_hours,
        
        -- Trigger analysis
        CASE 
            WHEN sick_calls > 0 THEN 'Sick Call'
            WHEN census > unit_baseline_census * 1.2 THEN 'High Census'
            WHEN actual_staff < scheduled_staff THEN 'Staffing Gap'
            ELSE 'Other'
        END AS overtime_trigger
        
    FROM staffing_daily
    WHERE date >= CURRENT_DATE - INTERVAL '3 months'
        AND (overtime_hours > 0 OR agency_hours > 0)
)
SELECT 
    decision_period,
    COUNT(*) AS occurrences,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_total,
    SUM(overtime_hours) AS total_overtime_hours,
    SUM(agency_hours) AS total_agency_hours,
    AVG(overtime_hours) AS avg_overtime_per_occurrence,
    AVG(agency_hours) AS avg_agency_per_occurrence
FROM premium_labor
GROUP BY decision_period
ORDER BY 
    CASE decision_period
        WHEN 'Morning' THEN 1
        WHEN 'Midday' THEN 2
        WHEN 'Afternoon Crisis' THEN 3
        WHEN 'Evening' THEN 4
        WHEN 'Night' THEN 5
    END;

-- ============================================================================
-- 5. COST IMPACT ANALYSIS
-- ============================================================================
-- Calculates financial impact of staffing variance

WITH cost_analysis AS (
    SELECT 
        date,
        unit_id,
        unit_name,
        
        -- Regular hours (assuming 12-hour shifts)
        scheduled_staff * 12 AS regular_hours,
        
        -- Premium hours
        overtime_hours,
        agency_hours,
        
        -- Cost calculations (using standard rates)
        scheduled_staff * 12 * 45 AS regular_cost,
        overtime_hours * 67.50 AS overtime_cost,
        agency_hours * 110 AS agency_cost,
        
        -- Excess costs (premiums only)
        overtime_hours * (67.50 - 45) AS overtime_premium,
        agency_hours * (110 - 45) AS agency_premium
        
    FROM staffing_daily
    WHERE date >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT 
    unit_name,
    COUNT(DISTINCT date) AS days_analyzed,
    
    -- Total hours
    SUM(regular_hours) AS total_regular_hours,
    SUM(overtime_hours) AS total_overtime_hours,
    SUM(agency_hours) AS total_agency_hours,
    
    -- Percentage of premium hours
    ROUND(100.0 * SUM(overtime_hours) / NULLIF(SUM(regular_hours), 0), 1) AS overtime_pct,
    ROUND(100.0 * SUM(agency_hours) / NULLIF(SUM(regular_hours), 0), 1) AS agency_pct,
    
    -- Costs
    SUM(regular_cost) AS total_regular_cost,
    SUM(overtime_premium) AS total_overtime_premium,
    SUM(agency_premium) AS total_agency_premium,
    SUM(overtime_premium + agency_premium) AS total_excess_cost,
    
    -- Annualized projection
    SUM(overtime_premium + agency_premium) * 365.0 / COUNT(DISTINCT date) AS annual_excess_cost_projection
    
FROM cost_analysis
GROUP BY unit_name
ORDER BY annual_excess_cost_projection DESC;

-- ============================================================================
-- 6. VARIANCE TRENDING AND FORECASTING
-- ============================================================================
-- Tracks variance trends over time for pattern detection

WITH variance_trends AS (
    SELECT 
        DATE_TRUNC('week', date) AS week_start,
        unit_id,
        unit_name,
        
        -- Weekly averages
        AVG(ABS(actual_staff - CEIL(census / 4.0))) AS avg_absolute_variance,
        STDDEV(actual_staff - CEIL(census / 4.0)) AS variance_volatility,
        
        -- Understaffing frequency
        SUM(CASE WHEN actual_staff < CEIL(census / 4.0) THEN 1 ELSE 0 END) AS understaffed_shifts,
        COUNT(*) AS total_shifts,
        
        -- Premium labor reliance
        SUM(overtime_hours) AS weekly_overtime,
        SUM(agency_hours) AS weekly_agency,
        
        -- Trend calculation (week over week change)
        LAG(AVG(ABS(actual_staff - CEIL(census / 4.0))), 1) OVER (
            PARTITION BY unit_id ORDER BY DATE_TRUNC('week', date)
        ) AS prev_week_variance
        
    FROM staffing_daily
    WHERE date >= CURRENT_DATE - INTERVAL '12 weeks'
    GROUP BY DATE_TRUNC('week', date), unit_id, unit_name
)
SELECT 
    week_start,
    unit_name,
    ROUND(avg_absolute_variance, 2) AS avg_variance,
    ROUND(variance_volatility, 2) AS volatility,
    ROUND(100.0 * understaffed_shifts / total_shifts, 1) AS pct_understaffed,
    ROUND(weekly_overtime, 1) AS overtime_hours,
    ROUND(weekly_agency, 1) AS agency_hours,
    CASE 
        WHEN prev_week_variance IS NULL THEN 'Baseline'
        WHEN avg_absolute_variance < prev_week_variance THEN 'Improving'
        WHEN avg_absolute_variance > prev_week_variance THEN 'Worsening'
        ELSE 'Stable'
    END AS trend_direction
FROM variance_trends
ORDER BY week_start DESC, unit_name;

-- ============================================================================
-- 7. PREDICTIVE INDICATORS
-- ============================================================================
-- Identifies leading indicators of staffing crises

WITH crisis_indicators AS (
    SELECT 
        s1.date,
        s1.unit_id,
        s1.unit_name,
        s1.shift,
        
        -- Current day metrics
        s1.census,
        s1.actual_staff,
        s1.overtime_hours,
        
        -- Previous day metrics
        LAG(s1.census, 1) OVER (PARTITION BY s1.unit_id ORDER BY s1.date) AS prev_census,
        LAG(s1.overtime_hours, 1) OVER (PARTITION BY s1.unit_id ORDER BY s1.date) AS prev_overtime,
        
        -- 7-day trailing indicators
        AVG(s1.census) OVER (
            PARTITION BY s1.unit_id 
            ORDER BY s1.date 
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) AS avg_census_7d,
        
        SUM(s1.overtime_hours) OVER (
            PARTITION BY s1.unit_id 
            ORDER BY s1.date 
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) AS total_overtime_7d,
        
        -- Crisis flag (high overtime day)
        CASE WHEN s1.overtime_hours > 24 THEN 1 ELSE 0 END AS is_crisis_day
        
    FROM staffing_daily s1
    WHERE s1.date >= CURRENT_DATE - INTERVAL '6 months'
)
SELECT 
    -- Indicators correlated with crisis days
    CASE WHEN is_crisis_day = 1 THEN 'Crisis' ELSE 'Normal' END AS day_type,
    
    AVG(CASE WHEN prev_overtime > 0 THEN 1 ELSE 0 END) AS pct_preceded_by_overtime,
    AVG(census - prev_census) AS avg_census_change,
    AVG(total_overtime_7d) AS avg_7d_overtime_before,
    AVG(census - avg_census_7d) AS avg_census_vs_7d_avg,
    
    COUNT(*) AS day_count
    
FROM crisis_indicators
WHERE prev_census IS NOT NULL
GROUP BY is_crisis_day
ORDER BY day_type DESC;

-- ============================================================================
-- 8. REBALANCING OPPORTUNITIES
-- ============================================================================
-- Identifies opportunities for staff rebalancing between units

WITH unit_status AS (
    SELECT 
        date,
        shift,
        unit_id,
        unit_name,
        census,
        actual_staff,
        CEIL(census / 4.0) AS required_staff,
        actual_staff - CEIL(census / 4.0) AS surplus_deficit,
        
        CASE 
            WHEN actual_staff > CEIL(census / 4.0) + 1 THEN 'Surplus'
            WHEN actual_staff < CEIL(census / 4.0) THEN 'Deficit'
            ELSE 'Balanced'
        END AS status
        
    FROM staffing_daily
    WHERE date = CURRENT_DATE
)
SELECT 
    s1.shift,
    s1.unit_name AS surplus_unit,
    s1.surplus_deficit AS available_staff,
    s2.unit_name AS deficit_unit,
    ABS(s2.surplus_deficit) AS staff_needed,
    LEAST(s1.surplus_deficit, ABS(s2.surplus_deficit)) AS rebalance_opportunity
FROM unit_status s1
JOIN unit_status s2 
    ON s1.date = s2.date 
    AND s1.shift = s2.shift
    AND s1.status = 'Surplus'
    AND s2.status = 'Deficit'
WHERE s1.unit_id != s2.unit_id
ORDER BY rebalance_opportunity DESC;

-- ============================================================================
-- 9. FLEX POOL REQUIREMENTS
-- ============================================================================
-- Calculates optimal flex pool size based on historical variance

WITH flex_requirements AS (
    SELECT 
        shift,
        date,
        SUM(GREATEST(CEIL(census / 4.0) - actual_staff, 0)) AS total_deficit,
        SUM(CASE WHEN actual_staff < CEIL(census / 4.0) THEN 1 ELSE 0 END) AS units_short
    FROM staffing_daily
    WHERE date >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY shift, date
)
SELECT 
    shift,
    
    -- Distribution of daily deficits
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_deficit) AS median_deficit,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_deficit) AS p75_deficit,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY total_deficit) AS p90_deficit,
    MAX(total_deficit) AS max_deficit,
    
    -- Frequency of deficits
    SUM(CASE WHEN total_deficit > 0 THEN 1 ELSE 0 END) AS days_with_deficit,
    COUNT(*) AS total_days,
    ROUND(100.0 * SUM(CASE WHEN total_deficit > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_days_deficit,
    
    -- Recommended flex pool size
    CEIL(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_deficit)) AS recommended_flex_pool,
    CEIL(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY total_deficit)) AS conservative_flex_pool
    
FROM flex_requirements
GROUP BY shift
ORDER BY shift;