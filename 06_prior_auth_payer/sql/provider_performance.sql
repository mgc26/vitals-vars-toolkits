-- Provider Performance Analysis for Gold-Carding
-- Identify providers eligible for auto-approval programs based on historical performance

WITH provider_pa_metrics AS (
    SELECT 
        p.provider_id,
        p.provider_name,
        p.provider_type,
        p.provider_specialty,
        pr.network_tier,
        COUNT(DISTINCT pa.pa_id) AS total_pas,
        COUNT(DISTINCT pa.member_id) AS unique_members,
        COUNT(DISTINCT pa.service_code) AS service_variety,
        
        -- Approval metrics
        SUM(CASE WHEN pa.status = 'APPROVED' THEN 1 ELSE 0 END)::FLOAT / COUNT(*) AS approval_rate,
        SUM(CASE WHEN pa.status = 'DENIED' THEN 1 ELSE 0 END) AS total_denials,
        
        -- Appeal metrics
        SUM(CASE WHEN pa.appeal_flag = 1 THEN 1 ELSE 0 END) AS total_appeals,
        SUM(CASE WHEN pa.appeal_flag = 1 AND pa.appeal_overturned = 1 THEN 1 ELSE 0 END) AS overturned_appeals,
        
        -- Quality metrics
        AVG(CASE WHEN pa.clinical_documentation_complete = 1 THEN 1 ELSE 0 END) AS doc_completeness_rate,
        AVG(CASE WHEN pa.meets_medical_necessity = 1 THEN 1 ELSE 0 END) AS medical_necessity_rate,
        
        -- Efficiency metrics
        AVG(EXTRACT(EPOCH FROM (pa.decision_date - pa.created_date))/3600) AS avg_hours_to_decision,
        SUM(CASE WHEN pa.expedited_flag = 1 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) AS expedited_rate,
        
        -- Time period
        MIN(pa.created_date) AS first_pa_date,
        MAX(pa.created_date) AS last_pa_date,
        EXTRACT(DAYS FROM MAX(pa.created_date) - MIN(pa.created_date)) AS days_active
        
    FROM prior_authorizations pa
    JOIN providers p ON pa.provider_id = p.provider_id
    LEFT JOIN provider_contracts pr ON p.provider_id = pr.provider_id 
        AND pr.effective_date <= CURRENT_DATE 
        AND (pr.termination_date IS NULL OR pr.termination_date > CURRENT_DATE)
    WHERE pa.created_date >= CURRENT_DATE - INTERVAL '24 months'
    GROUP BY 1, 2, 3, 4, 5
),
provider_scoring AS (
    SELECT 
        *,
        -- Calculate gold card eligibility score
        CASE 
            WHEN total_pas < 50 THEN 0  -- Minimum volume threshold
            WHEN approval_rate >= 0.92 AND days_active >= 365 THEN 100
            WHEN approval_rate >= 0.90 AND doc_completeness_rate >= 0.95 THEN 90
            WHEN approval_rate >= 0.88 AND medical_necessity_rate >= 0.95 THEN 80
            WHEN approval_rate >= 0.85 AND overturned_appeals > total_denials * 0.5 THEN 70
            ELSE approval_rate * 100 * 0.7  -- Partial score
        END AS gold_card_score,
        
        -- Risk assessment
        CASE 
            WHEN total_appeals > 0 THEN overturned_appeals::FLOAT / total_appeals 
            ELSE NULL 
        END AS appeal_overturn_rate,
        
        -- Calculate potential impact
        total_pas * 14.49 AS current_annual_cost,
        total_pas * 1.50 AS automated_annual_cost,
        total_pas * (14.49 - 1.50) AS potential_annual_savings
        
    FROM provider_pa_metrics
),
gold_card_recommendations AS (
    SELECT 
        provider_id,
        provider_name,
        provider_type,
        provider_specialty,
        network_tier,
        total_pas,
        unique_members,
        service_variety,
        ROUND(approval_rate * 100, 1) AS approval_rate_pct,
        total_denials,
        total_appeals,
        ROUND(COALESCE(appeal_overturn_rate, 0) * 100, 1) AS appeal_overturn_rate_pct,
        ROUND(doc_completeness_rate * 100, 1) AS doc_completeness_pct,
        ROUND(avg_hours_to_decision, 1) AS avg_hours_to_decision,
        ROUND(gold_card_score, 1) AS gold_card_score,
        ROUND(potential_annual_savings, 0) AS potential_annual_savings,
        
        -- Final recommendation
        CASE 
            WHEN gold_card_score >= 90 THEN 'IMMEDIATE_GOLD_CARD'
            WHEN gold_card_score >= 80 THEN 'GOLD_CARD_ELIGIBLE'
            WHEN gold_card_score >= 70 THEN 'CONDITIONAL_GOLD_CARD'
            WHEN gold_card_score >= 60 AND total_pas >= 100 THEN 'COACHING_CANDIDATE'
            ELSE 'STANDARD_REVIEW'
        END AS recommendation,
        
        -- Recommended service lines for gold carding
        CASE 
            WHEN gold_card_score >= 80 THEN 'ALL_SERVICES'
            WHEN gold_card_score >= 70 AND provider_specialty IN ('PRIMARY_CARE', 'INTERNAL_MEDICINE') THEN 'ROUTINE_SERVICES'
            WHEN gold_card_score >= 70 THEN 'HIGH_APPROVAL_SERVICES'
            ELSE 'NONE'
        END AS gold_card_scope
        
    FROM provider_scoring
    WHERE total_pas >= 20  -- Minimum threshold for analysis
)
SELECT * FROM gold_card_recommendations
ORDER BY gold_card_score DESC, potential_annual_savings DESC;

-- Summary Report
WITH summary AS (
    SELECT 
        recommendation,
        COUNT(*) AS provider_count,
        SUM(total_pas) AS total_pa_volume,
        ROUND(AVG(approval_rate_pct), 1) AS avg_approval_rate,
        ROUND(SUM(potential_annual_savings), 0) AS total_savings_opportunity
    FROM gold_card_recommendations
    GROUP BY recommendation
)
SELECT 
    'GOLD CARD OPPORTUNITY SUMMARY' AS report_type,
    SUM(CASE WHEN recommendation IN ('IMMEDIATE_GOLD_CARD', 'GOLD_CARD_ELIGIBLE') THEN provider_count ELSE 0 END) AS eligible_providers,
    SUM(CASE WHEN recommendation IN ('IMMEDIATE_GOLD_CARD', 'GOLD_CARD_ELIGIBLE') THEN total_pa_volume ELSE 0 END) AS eligible_pa_volume,
    ROUND(SUM(CASE WHEN recommendation IN ('IMMEDIATE_GOLD_CARD', 'GOLD_CARD_ELIGIBLE') THEN total_savings_opportunity ELSE 0 END), 0) AS immediate_savings_opportunity
FROM summary;