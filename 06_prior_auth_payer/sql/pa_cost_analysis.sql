-- Prior Authorization Cost Analysis
-- Calculate current costs per PA by type and identify savings opportunities

WITH pa_volumes AS (
    SELECT 
        DATE_TRUNC('month', pa.created_date) AS month,
        pa.submission_method,
        pa.service_category,
        COUNT(*) AS pa_count,
        AVG(EXTRACT(EPOCH FROM (pa.decision_date - pa.created_date))/3600) AS avg_hours_to_decision,
        SUM(CASE WHEN pa.status = 'APPROVED' THEN 1 ELSE 0 END)::FLOAT / COUNT(*) AS approval_rate,
        SUM(CASE WHEN pa.appeal_flag = 1 AND pa.appeal_overturned = 1 THEN 1 ELSE 0 END)::FLOAT / 
            NULLIF(SUM(CASE WHEN pa.appeal_flag = 1 THEN 1 ELSE 0 END), 0) AS appeal_overturn_rate
    FROM prior_authorizations pa
    WHERE pa.created_date >= CURRENT_DATE - INTERVAL '12 months'
    GROUP BY 1, 2, 3
),
processing_costs AS (
    SELECT
        submission_method,
        CASE 
            WHEN submission_method = 'FAX' THEN 14.49
            WHEN submission_method = 'PHONE' THEN 14.49
            WHEN submission_method = 'PORTAL' THEN 8.09
            WHEN submission_method = 'API' THEN 3.50
            WHEN submission_method = 'AI_AUTOMATED' THEN 1.50
            ELSE 14.49
        END AS cost_per_pa,
        CASE 
            WHEN submission_method IN ('FAX', 'PHONE') THEN 'MANUAL'
            WHEN submission_method = 'PORTAL' THEN 'SEMI_AUTOMATED'
            WHEN submission_method IN ('API', 'AI_AUTOMATED') THEN 'AUTOMATED'
            ELSE 'MANUAL'
        END AS automation_level
    FROM (SELECT DISTINCT submission_method FROM pa_volumes) methods
),
cost_summary AS (
    SELECT 
        v.month,
        v.submission_method,
        pc.automation_level,
        v.service_category,
        v.pa_count,
        v.avg_hours_to_decision,
        v.approval_rate,
        v.appeal_overturn_rate,
        pc.cost_per_pa,
        v.pa_count * pc.cost_per_pa AS total_cost,
        -- Calculate potential savings if converted to automated
        v.pa_count * (pc.cost_per_pa - 1.50) AS potential_savings_to_ai,
        v.pa_count * (pc.cost_per_pa - 3.50) AS potential_savings_to_api
    FROM pa_volumes v
    JOIN processing_costs pc ON v.submission_method = pc.submission_method
)
SELECT 
    month,
    automation_level,
    submission_method,
    service_category,
    pa_count,
    ROUND(avg_hours_to_decision, 1) AS avg_hours_to_decision,
    ROUND(approval_rate * 100, 1) AS approval_rate_pct,
    ROUND(COALESCE(appeal_overturn_rate, 0) * 100, 1) AS appeal_overturn_rate_pct,
    ROUND(cost_per_pa, 2) AS cost_per_pa,
    ROUND(total_cost, 0) AS total_monthly_cost,
    ROUND(potential_savings_to_api, 0) AS savings_if_api,
    ROUND(potential_savings_to_ai, 0) AS savings_if_ai_automated,
    -- Calculate ROI metrics
    CASE 
        WHEN approval_rate >= 0.95 THEN 'ELIMINATE_PA'
        WHEN approval_rate >= 0.92 THEN 'GOLD_CARD_ELIGIBLE'
        WHEN approval_rate >= 0.85 AND automation_level = 'MANUAL' THEN 'AUTOMATE_PRIORITY'
        ELSE 'MAINTAIN_REVIEW'
    END AS optimization_recommendation
FROM cost_summary
ORDER BY month DESC, total_monthly_cost DESC;

-- Summary Statistics
WITH totals AS (
    SELECT 
        automation_level,
        SUM(pa_count) AS total_pas,
        SUM(total_cost) AS total_cost,
        SUM(potential_savings_to_ai) AS total_potential_savings
    FROM cost_summary
    GROUP BY automation_level
)
SELECT 
    'EXECUTIVE SUMMARY' AS report_section,
    SUM(total_pas) AS annual_pa_volume,
    ROUND(SUM(total_cost), 0) AS annual_pa_cost,
    ROUND(SUM(total_cost) / SUM(total_pas), 2) AS avg_cost_per_pa,
    ROUND(SUM(CASE WHEN automation_level = 'MANUAL' THEN total_pas ELSE 0 END)::FLOAT / 
          SUM(total_pas) * 100, 1) AS manual_pa_percentage,
    ROUND(SUM(total_potential_savings), 0) AS annual_savings_opportunity,
    ROUND(SUM(total_potential_savings) / SUM(total_cost) * 100, 1) AS potential_cost_reduction_pct
FROM totals;