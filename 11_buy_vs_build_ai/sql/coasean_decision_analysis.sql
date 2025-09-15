-- Coasean Build vs. Buy Decision Analysis SQL Queries
-- Based on Ronald Coase's Transaction Cost Economics
-- For analyzing your organization's AI/analytics project decisions

-- ============================================================================
-- Query 1: Project Portfolio Transaction Cost Assessment
-- Evaluates current projects through the Coasean lens
-- ============================================================================

WITH project_factors AS (
    SELECT
        project_name,
        project_type,

        -- Coasean Factor Scoring (1-5 scale)
        spec_volatility_score,        -- How often requirements change
        verification_difficulty_score, -- How hard to verify quality
        interdependence_score,         -- Coupling with other systems
        data_sensitivity_score,        -- PHI/IP sensitivity
        supplier_power_score,          -- Vendor lock-in risk
        frequency_tempo_score,         -- How often you use it

        -- Calculate weighted Coasean score
        -- Higher score = Build, Lower score = Buy
        (spec_volatility_score * 1.0 +
         verification_difficulty_score * 1.0 +
         interdependence_score * 1.0 +
         data_sensitivity_score * 1.5 +  -- HIPAA weight
         supplier_power_score * 1.0 +
         frequency_tempo_score * 1.0) AS total_coasean_score,

        -- Current approach
        current_approach, -- 'BUILD', 'BUY', 'HYBRID'

        -- Financial metrics
        annual_cost,
        implementation_months,
        maintenance_fte

    FROM ai_projects
    WHERE status = 'ACTIVE'
),

decision_recommendations AS (
    SELECT
        *,
        CASE
            WHEN total_coasean_score <= 13 THEN 'STRONG BUY'
            WHEN total_coasean_score <= 16 THEN 'LEAN BUY'
            WHEN total_coasean_score <= 19 THEN 'HYBRID'
            WHEN total_coasean_score <= 22 THEN 'LEAN BUILD'
            ELSE 'STRONG BUILD'
        END AS recommended_approach,

        CASE
            WHEN total_coasean_score <= 15 THEN 'LOW - Market transactions efficient'
            WHEN total_coasean_score <= 20 THEN 'MEDIUM - Consider hybrid'
            ELSE 'HIGH - Internal coordination cheaper'
        END AS transaction_cost_level

    FROM project_factors
)

SELECT
    project_name,
    project_type,
    total_coasean_score,
    current_approach,
    recommended_approach,
    transaction_cost_level,

    -- Flag misalignments
    CASE
        WHEN current_approach != recommended_approach THEN 'MISALIGNED'
        ELSE 'ALIGNED'
    END AS alignment_status,

    -- Estimate potential savings from realignment
    CASE
        WHEN current_approach = 'BUILD' AND recommended_approach LIKE '%BUY%'
        THEN annual_cost * 0.4  -- Typical 40% savings from buy
        WHEN current_approach = 'BUY' AND recommended_approach LIKE '%BUILD%'
        THEN annual_cost * 0.2  -- Potential 20% value from customization
        ELSE 0
    END AS potential_annual_savings

FROM decision_recommendations
ORDER BY
    alignment_status DESC,
    potential_annual_savings DESC;

-- ============================================================================
-- Query 2: Vendor Lock-in Risk Assessment
-- Calculates switching costs based on Coase's asset specificity concept
-- ============================================================================

WITH vendor_analysis AS (
    SELECT
        vendor_name,
        product_category,
        contract_start_date,

        -- Calculate time with vendor
        DATEDIFF(month, contract_start_date, GETDATE()) / 12.0 AS years_with_vendor,

        -- Count integration points
        COUNT(DISTINCT integration_system) AS integration_points,

        -- Annual costs
        annual_license_cost,

        -- Custom development on top of vendor
        custom_code_lines,
        custom_workflows_count

    FROM vendor_contracts vc
    LEFT JOIN vendor_integrations vi ON vc.vendor_id = vi.vendor_id
    LEFT JOIN vendor_customizations vcu ON vc.vendor_id = vcu.vendor_id
    GROUP BY
        vendor_name,
        product_category,
        contract_start_date,
        annual_license_cost,
        custom_code_lines,
        custom_workflows_count
),

switching_cost_calculation AS (
    SELECT
        *,

        -- Calculate switching cost penalty (Coase's asset specificity)
        (years_with_vendor * 0.15 +           -- 15% per year
         integration_points * 0.10 +           -- 10% per integration
         custom_workflows_count * 0.05) AS switching_cost_multiplier,

        -- Estimate total switching cost
        annual_license_cost *
        (years_with_vendor * 0.15 +
         integration_points * 0.10 +
         custom_workflows_count * 0.05) AS estimated_switching_cost

    FROM vendor_analysis
)

SELECT
    vendor_name,
    product_category,
    years_with_vendor,
    integration_points,
    switching_cost_multiplier,
    estimated_switching_cost,

    -- Risk level based on switching costs
    CASE
        WHEN switching_cost_multiplier < 0.5 THEN 'LOW RISK'
        WHEN switching_cost_multiplier < 1.0 THEN 'MEDIUM RISK'
        WHEN switching_cost_multiplier < 1.5 THEN 'HIGH RISK'
        ELSE 'CRITICAL RISK'
    END AS vendor_lock_in_risk,

    -- Coase would say...
    CASE
        WHEN switching_cost_multiplier > 1.5
        THEN 'Transaction costs exceed market value - consider insourcing'
        WHEN switching_cost_multiplier > 1.0
        THEN 'High asset specificity - negotiate aggressively'
        ELSE 'Market remains efficient - maintain vendor relationship'
    END AS coasean_recommendation

FROM switching_cost_calculation
ORDER BY estimated_switching_cost DESC;

-- ============================================================================
-- Query 3: Build vs Buy Historical Performance Analysis
-- What would Coase say about your past decisions?
-- ============================================================================

WITH historical_projects AS (
    SELECT
        project_name,
        decision_type, -- 'BUILD' or 'BUY'

        -- Planned vs actual
        planned_cost,
        actual_cost,
        planned_months,
        actual_months,

        -- Success metrics
        objectives_met,
        user_satisfaction_score,

        -- Calculate overruns
        (actual_cost - planned_cost) / NULLIF(planned_cost, 0) AS cost_overrun_pct,
        (actual_months - planned_months) / NULLIF(planned_months, 0) AS time_overrun_pct

    FROM completed_projects
    WHERE completion_date > DATEADD(year, -3, GETDATE())
)

SELECT
    decision_type,
    COUNT(*) AS project_count,

    -- Success rates
    AVG(CASE WHEN objectives_met = 'YES' THEN 1.0 ELSE 0.0 END) AS success_rate,
    AVG(user_satisfaction_score) AS avg_satisfaction,

    -- Overrun analysis
    AVG(cost_overrun_pct) AS avg_cost_overrun,
    AVG(time_overrun_pct) AS avg_time_overrun,

    -- Variance (risk indicator)
    STDEV(cost_overrun_pct) AS cost_overrun_variance,
    STDEV(time_overrun_pct) AS time_overrun_variance,

    -- Transaction cost interpretation
    CASE
        WHEN decision_type = 'BUILD' AND AVG(cost_overrun_pct) > 0.5
        THEN 'High internal coordination costs - Coase suggests more buying'
        WHEN decision_type = 'BUY' AND AVG(user_satisfaction_score) < 3
        THEN 'High specification/verification costs - Coase suggests more building'
        ELSE 'Transaction costs appear balanced'
    END AS coasean_insight

FROM historical_projects
GROUP BY decision_type;

-- ============================================================================
-- Query 4: Identify Hybrid Opportunities
-- Where Coase would recommend splitting the difference
-- ============================================================================

SELECT
    capability_area,

    -- Components that should be bought (commodities)
    STRING_AGG(
        CASE
            WHEN is_commodity = 1 AND vendor_solutions > 3
            THEN component_name
        END, ', '
    ) AS buy_components,

    -- Components that should be built (differentiators)
    STRING_AGG(
        CASE
            WHEN is_proprietary = 1 OR requires_custom_workflow = 1
            THEN component_name
        END, ', '
    ) AS build_components,

    -- Calculate hybrid score
    SUM(CASE WHEN is_commodity = 1 THEN 1 ELSE 0 END) AS commodity_count,
    SUM(CASE WHEN is_proprietary = 1 THEN 1 ELSE 0 END) AS proprietary_count,

    -- Hybrid recommendation strength
    CASE
        WHEN SUM(CASE WHEN is_commodity = 1 THEN 1 ELSE 0 END) > 0
         AND SUM(CASE WHEN is_proprietary = 1 THEN 1 ELSE 0 END) > 0
        THEN 'STRONG HYBRID CANDIDATE'
        ELSE 'PURE APPROACH RECOMMENDED'
    END AS hybrid_recommendation

FROM capability_components
WHERE active = 1
GROUP BY capability_area
HAVING COUNT(*) > 1  -- Multi-component capabilities only
ORDER BY
    commodity_count DESC,
    proprietary_count DESC;