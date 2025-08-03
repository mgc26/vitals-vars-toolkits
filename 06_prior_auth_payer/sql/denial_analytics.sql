-- Denial Analytics and Pattern Recognition
-- Analyze denial patterns to reduce false positives and improve member experience

WITH denial_details AS (
    SELECT 
        pa.pa_id,
        pa.created_date,
        pa.provider_id,
        pa.member_id,
        pa.service_code,
        sc.service_description,
        sc.service_category,
        pa.denial_reason_code,
        dr.denial_reason_description,
        dr.denial_category,
        pa.appeal_flag,
        pa.appeal_overturned,
        pa.review_type,
        pa.reviewer_id,
        pa.clinical_reviewer_flag,
        m.member_age,
        m.risk_score,
        m.chronic_condition_count
    FROM prior_authorizations pa
    JOIN service_codes sc ON pa.service_code = sc.service_code
    JOIN denial_reasons dr ON pa.denial_reason_code = dr.denial_reason_code
    JOIN members m ON pa.member_id = m.member_id
    WHERE pa.status = 'DENIED'
        AND pa.created_date >= CURRENT_DATE - INTERVAL '12 months'
),
denial_patterns AS (
    SELECT 
        service_category,
        denial_category,
        denial_reason_code,
        denial_reason_description,
        COUNT(*) AS denial_count,
        SUM(appeal_flag) AS appeal_count,
        SUM(appeal_overturned) AS overturn_count,
        
        -- Calculate rates
        SUM(appeal_flag)::FLOAT / COUNT(*) AS appeal_rate,
        SUM(appeal_overturned)::FLOAT / NULLIF(SUM(appeal_flag), 0) AS overturn_rate,
        
        -- Member impact
        COUNT(DISTINCT member_id) AS affected_members,
        AVG(member_age) AS avg_member_age,
        AVG(risk_score) AS avg_risk_score,
        
        -- Review patterns
        SUM(CASE WHEN clinical_reviewer_flag = 1 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) AS clinical_review_rate,
        COUNT(DISTINCT reviewer_id) AS unique_reviewers
        
    FROM denial_details
    GROUP BY 1, 2, 3, 4
),
high_overturn_denials AS (
    SELECT 
        *,
        -- Calculate the cost of incorrect denials
        overturn_count * 43.84 AS appeal_processing_cost,
        denial_count * 14.49 AS total_review_cost,
        
        -- Flag problematic denial patterns
        CASE 
            WHEN overturn_rate >= 0.80 AND denial_count >= 10 THEN 'CRITICAL_REVIEW_NEEDED'
            WHEN overturn_rate >= 0.60 AND denial_count >= 20 THEN 'HIGH_FALSE_POSITIVE'
            WHEN overturn_rate >= 0.40 AND denial_count >= 50 THEN 'MODERATE_CONCERN'
            WHEN appeal_rate >= 0.50 THEN 'HIGH_PROVIDER_FRICTION'
            ELSE 'ACCEPTABLE'
        END AS denial_quality_flag,
        
        -- Recommend actions
        CASE 
            WHEN overturn_rate >= 0.80 THEN 'ELIMINATE_DENIAL_REASON'
            WHEN overturn_rate >= 0.60 AND clinical_review_rate < 0.5 THEN 'REQUIRE_CLINICAL_REVIEW'
            WHEN overturn_rate >= 0.50 THEN 'REVISE_CRITERIA'
            WHEN appeal_rate >= 0.60 THEN 'PROVIDER_EDUCATION'
            ELSE 'MONITOR'
        END AS recommended_action
        
    FROM denial_patterns
    WHERE denial_count >= 5  -- Minimum threshold for pattern analysis
),
-- Service-specific denial analysis
service_denial_summary AS (
    SELECT 
        dd.service_code,
        dd.service_description,
        COUNT(*) AS total_denials,
        COUNT(DISTINCT dd.provider_id) AS providers_affected,
        COUNT(DISTINCT dd.member_id) AS members_affected,
        SUM(dd.appeal_overturned) AS overturns,
        ROUND(SUM(dd.appeal_overturned)::FLOAT / NULLIF(SUM(dd.appeal_flag), 0) * 100, 1) AS overturn_rate_pct,
        
        -- Most common denial reason
        MODE() WITHIN GROUP (ORDER BY dd.denial_reason_description) AS primary_denial_reason,
        
        -- Calculate if this service should be auto-approved
        CASE 
            WHEN SUM(dd.appeal_overturned)::FLOAT / NULLIF(SUM(dd.appeal_flag), 0) >= 0.75 
                 AND COUNT(*) >= 20 THEN 'RECOMMEND_AUTO_APPROVE'
            WHEN SUM(dd.appeal_overturned)::FLOAT / NULLIF(SUM(dd.appeal_flag), 0) >= 0.60 
                 AND COUNT(*) >= 50 THEN 'REVIEW_CRITERIA'
            ELSE 'MAINTAIN_CURRENT'
        END AS service_recommendation
        
    FROM denial_details dd
    GROUP BY 1, 2
    HAVING COUNT(*) >= 10
)
-- Main output
SELECT 
    denial_category,
    service_category,
    denial_reason_description,
    denial_count,
    appeal_count,
    overturn_count,
    ROUND(appeal_rate * 100, 1) AS appeal_rate_pct,
    ROUND(COALESCE(overturn_rate, 0) * 100, 1) AS overturn_rate_pct,
    affected_members,
    ROUND(clinical_review_rate * 100, 1) AS clinical_review_rate_pct,
    denial_quality_flag,
    recommended_action,
    ROUND(appeal_processing_cost, 0) AS appeal_cost,
    ROUND(total_review_cost, 0) AS review_cost
FROM high_overturn_denials
WHERE denial_quality_flag != 'ACCEPTABLE'
ORDER BY overturn_rate DESC, denial_count DESC;

-- Executive Summary
WITH denial_summary AS (
    SELECT 
        COUNT(*) AS total_denials,
        SUM(appeal_flag) AS total_appeals,
        SUM(appeal_overturned) AS total_overturns,
        SUM(appeal_overturned)::FLOAT / NULLIF(SUM(appeal_flag), 0) AS overall_overturn_rate,
        COUNT(DISTINCT member_id) AS members_impacted,
        SUM(appeal_overturned) * 43.84 AS total_appeal_cost
    FROM denial_details
)
SELECT 
    'DENIAL QUALITY REPORT' AS report_type,
    total_denials,
    total_appeals,
    total_overturns,
    ROUND(overall_overturn_rate * 100, 1) AS overturn_rate_pct,
    members_impacted,
    ROUND(total_appeal_cost, 0) AS annual_appeal_processing_cost,
    ROUND(total_overturns::FLOAT / total_denials * 100, 1) AS false_positive_rate_pct
FROM denial_summary;