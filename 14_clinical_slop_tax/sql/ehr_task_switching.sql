/*
EHR Task-Switching Analysis
Measures how frequently clinicians switch between tasks, charts, and system modules

IMPORTANT: This is a template. You will need to adapt table names and field names
to your specific EHR vendor (Epic, Cerner, Meditech, etc.)

Metrics Calculated:
1. Task switches per hour (overall)
2. Within-chart task switches (jumping between tabs/sections)
3. Between-chart switches (changing patients)
4. Switches by time of day
5. High-fragmentation clinicians (who's struggling most)
*/

-- ==============================================================================
-- QUERY 1: Task Switches Per Hour by Clinician Type
-- ==============================================================================
-- Identifies overall task-switching frequency
-- Benchmark: >150 switches/hour = high fragmentation, >100 = moderate concern

WITH ehr_events AS (
    SELECT
        user_id,
        user_role,
        event_timestamp,
        activity_type,
        patient_id,
        module_name,
        LAG(activity_type) OVER (PARTITION BY user_id, DATE(event_timestamp)
                                  ORDER BY event_timestamp) AS previous_activity,
        LAG(module_name) OVER (PARTITION BY user_id, DATE(event_timestamp)
                               ORDER BY event_timestamp) AS previous_module,
        LAG(event_timestamp) OVER (PARTITION BY user_id, DATE(event_timestamp)
                                    ORDER BY event_timestamp) AS previous_timestamp
    FROM ehr_audit_log  -- Replace with your EHR's event log table
    WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
      AND user_role IN ('Physician', 'Nurse', 'APP')  -- Adjust role names
      AND activity_type NOT IN ('Login', 'Logout', 'Idle')  -- Filter out non-work events
)

SELECT
    user_role,
    COUNT(DISTINCT user_id) AS clinician_count,
    COUNT(CASE WHEN activity_type != previous_activity OR module_name != previous_module
               THEN 1 END) AS total_task_switches,
    ROUND(SUM(EXTRACT(EPOCH FROM (event_timestamp - previous_timestamp)) / 3600), 2) AS total_hours,
    ROUND(COUNT(CASE WHEN activity_type != previous_activity OR module_name != previous_module
                     THEN 1 END)::NUMERIC /
          NULLIF(SUM(EXTRACT(EPOCH FROM (event_timestamp - previous_timestamp)) / 3600), 0),
          1) AS avg_task_switches_per_hour,
    ROUND(3600.0 / NULLIF(COUNT(CASE WHEN activity_type != previous_activity OR module_name != previous_module
                                     THEN 1 END)::NUMERIC /
                          SUM(EXTRACT(EPOCH FROM (event_timestamp - previous_timestamp)) / 3600), 0),
          0) AS avg_seconds_per_task
FROM ehr_events
WHERE previous_activity IS NOT NULL
GROUP BY user_role
ORDER BY avg_task_switches_per_hour DESC;


-- ==============================================================================
-- QUERY 2: Within-Chart vs Between-Chart Task Switches
-- ==============================================================================
-- Differentiates cognitive switching within one patient vs. switching patients
-- High within-chart switching = poor EHR navigation design

WITH ehr_events AS (
    SELECT
        user_id,
        user_role,
        event_timestamp,
        patient_id,
        module_name,
        LAG(patient_id) OVER (PARTITION BY user_id, DATE(event_timestamp)
                              ORDER BY event_timestamp) AS previous_patient_id,
        LAG(module_name) OVER (PARTITION BY user_id, DATE(event_timestamp)
                               ORDER BY event_timestamp) AS previous_module
    FROM ehr_audit_log
    WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
      AND user_role IN ('Physician', 'Nurse', 'APP')
      AND patient_id IS NOT NULL
)

SELECT
    user_role,
    COUNT(CASE WHEN patient_id = previous_patient_id AND module_name != previous_module
               THEN 1 END) AS within_chart_switches,
    COUNT(CASE WHEN patient_id != previous_patient_id
               THEN 1 END) AS between_chart_switches,
    ROUND(COUNT(CASE WHEN patient_id = previous_patient_id AND module_name != previous_module
                     THEN 1 END)::NUMERIC /
          NULLIF(COUNT(DISTINCT user_id), 0),
          1) AS avg_within_chart_per_clinician,
    ROUND(COUNT(CASE WHEN patient_id != previous_patient_id
                     THEN 1 END)::NUMERIC /
          NULLIF(COUNT(DISTINCT user_id), 0),
          1) AS avg_between_chart_per_clinician
FROM ehr_events
WHERE previous_patient_id IS NOT NULL
GROUP BY user_role
ORDER BY within_chart_switches DESC;


-- ==============================================================================
-- QUERY 3: Documentation Time Trending
-- ==============================================================================
-- Tracks how much time clinicians spend on documentation over time
-- Look for upward trends (getting worse) or impact of interventions

SELECT
    DATE_TRUNC('week', event_timestamp) AS week_start,
    user_role,
    COUNT(DISTINCT user_id) AS clinician_count,
    ROUND(SUM(CASE WHEN activity_type IN ('Documentation', 'Chart Review', 'Note Writing')
                   THEN time_spent_seconds END) / 3600.0, 1) AS documentation_hours,
    ROUND(SUM(time_spent_seconds) / 3600.0, 1) AS total_ehr_hours,
    ROUND((SUM(CASE WHEN activity_type IN ('Documentation', 'Chart Review', 'Note Writing')
                    THEN time_spent_seconds END)::NUMERIC /
           NULLIF(SUM(time_spent_seconds), 0)) * 100,
          1) AS pct_time_on_documentation
FROM ehr_audit_log
WHERE event_timestamp >= CURRENT_DATE - INTERVAL '90 days'
  AND user_role IN ('Physician', 'Nurse', 'APP')
  AND time_spent_seconds > 0
GROUP BY DATE_TRUNC('week', event_timestamp), user_role
ORDER BY week_start DESC, user_role;


-- ==============================================================================
-- QUERY 4: After-Hours EHR Work
-- ==============================================================================
-- Identifies work done outside scheduled shifts (sign of incomplete workflows)
-- Benchmark from research: Mean 27-34 minutes per day after-hours work

WITH shift_definitions AS (
    -- Customize these based on your organization's shift times
    SELECT
        'Day Shift' AS shift_name,
        '07:00'::TIME AS shift_start,
        '19:00'::TIME AS shift_end
    UNION ALL
    SELECT 'Night Shift', '19:00'::TIME, '07:00'::TIME
),

ehr_activity AS (
    SELECT
        user_id,
        user_role,
        DATE(event_timestamp) AS work_date,
        event_timestamp::TIME AS work_time,
        time_spent_seconds,
        -- Simple after-hours definition: before 7am or after 7pm for day shift
        CASE WHEN event_timestamp::TIME < '07:00'::TIME
                  OR event_timestamp::TIME > '19:00'::TIME
             THEN true ELSE false END AS is_after_hours
    FROM ehr_audit_log
    WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
      AND user_role IN ('Physician', 'Nurse', 'APP')
      AND time_spent_seconds > 0
)

SELECT
    user_role,
    COUNT(DISTINCT user_id) AS clinician_count,
    ROUND(AVG(CASE WHEN is_after_hours THEN time_spent_seconds ELSE 0 END) / 60.0, 1) AS avg_after_hours_minutes_per_day,
    ROUND((SUM(CASE WHEN is_after_hours THEN time_spent_seconds END)::NUMERIC /
           NULLIF(SUM(time_spent_seconds), 0)) * 100,
          1) AS pct_work_after_hours,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CASE WHEN is_after_hours THEN time_spent_seconds END) / 60.0 AS median_after_hours_minutes
FROM ehr_activity
GROUP BY user_role
ORDER BY avg_after_hours_minutes_per_day DESC;


-- ==============================================================================
-- QUERY 5: Identify High-Fragmentation Clinicians
-- ==============================================================================
-- Pinpoints individuals experiencing the worst task-switching burden
-- Use for targeted workflow redesign or 1:1 support

WITH user_switches AS (
    SELECT
        user_id,
        user_role,
        department,
        COUNT(CASE WHEN activity_type != LAG(activity_type)
                           OVER (PARTITION BY user_id, DATE(event_timestamp)
                                 ORDER BY event_timestamp)
                   THEN 1 END) AS daily_task_switches,
        SUM(time_spent_seconds) / 3600.0 AS daily_hours,
        DATE(event_timestamp) AS work_date
    FROM ehr_audit_log
    WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
      AND user_role IN ('Physician', 'Nurse', 'APP')
    GROUP BY user_id, user_role, department, DATE(event_timestamp)
    HAVING SUM(time_spent_seconds) >= 14400  -- At least 4 hours of EHR work
)

SELECT
    user_id,
    user_role,
    department,
    COUNT(*) AS days_observed,
    ROUND(AVG(daily_task_switches), 1) AS avg_task_switches_per_day,
    ROUND(AVG(daily_task_switches / NULLIF(daily_hours, 0)), 1) AS avg_switches_per_hour,
    MAX(daily_task_switches) AS max_switches_in_one_day,
    ROUND(AVG(daily_hours), 1) AS avg_ehr_hours_per_day
FROM user_switches
GROUP BY user_id, user_role, department
HAVING AVG(daily_task_switches / NULLIF(daily_hours, 0)) > 100  -- Flag >100 switches/hour
ORDER BY avg_switches_per_hour DESC
LIMIT 50;


-- ==============================================================================
-- QUERY 6: Module Navigation Patterns (Clinical Slop Hotspots)
-- ==============================================================================
-- Identifies which EHR modules require the most back-and-forth navigation
-- High switching between specific modules = workflow design problem

WITH module_transitions AS (
    SELECT
        module_name AS from_module,
        LEAD(module_name) OVER (PARTITION BY user_id, DATE(event_timestamp)
                                ORDER BY event_timestamp) AS to_module,
        user_role
    FROM ehr_audit_log
    WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
      AND user_role IN ('Physician', 'Nurse', 'APP')
      AND module_name IS NOT NULL
)

SELECT
    from_module,
    to_module,
    user_role,
    COUNT(*) AS transition_count,
    RANK() OVER (PARTITION BY user_role ORDER BY COUNT(*) DESC) AS rank_within_role
FROM module_transitions
WHERE from_module != to_module  -- Exclude same-module events
  AND to_module IS NOT NULL
GROUP BY from_module, to_module, user_role
HAVING COUNT(*) > 100  -- Filter low-frequency transitions
ORDER BY user_role, transition_count DESC
LIMIT 100;


-- ==============================================================================
-- USAGE NOTES
-- ==============================================================================
/*
1. Table/Field Customization Required:
   - Replace 'ehr_audit_log' with your EHR's event tracking table
   - Adjust field names (user_id, activity_type, module_name, etc.)
   - Modify user_role values to match your system
   - Update shift time definitions in Query 4

2. Performance Optimization:
   - Add indexes on: event_timestamp, user_id, user_role, patient_id
   - Consider materialized views for 30/90-day windows
   - Use partitioning by date if table is very large

3. Interpretation:
   - Task switches per hour >150 = crisis, >100 = concern, <80 = good
   - After-hours work >40 minutes/day = workflow completion problem
   - High within-chart switching = poor EHR design
   - Module transition patterns reveal "slop hotspots"

4. Action Triggers:
   - If avg_task_switches_per_hour > 150: Immediate workflow audit needed
   - If pct_time_on_documentation > 50%: Documentation optimization priority
   - If pct_work_after_hours > 20%: Handoff/workflow completion issue
*/
