-- SDOH Signal Clustering SQL Templates
-- Vitals & Variables Edition 18: Care Management AI vs. Member Reality
--
-- These queries cluster members by social determinant signals from claims data.
-- Based on research showing dose-response relationship: 3+ social risk factors
-- correlate with 3.26x higher odds of nonadherence (Berkowitz et al., 2020).
--
-- Key insight: These are structural conditions, not personal failings.
-- Use clustering to match intervention capacity to actual barriers.

-- ============================================================================
-- QUERY 1: Z-Code Based SDOH Signal Detection
-- ICD-10-CM Z55-Z65 codes capture social determinants documented in encounters
-- ============================================================================
WITH sdoh_codes AS (
    SELECT
        c.member_id,
        c.claim_date,
        c.diagnosis_code,
        CASE
            -- Housing instability (Z59.x)
            WHEN c.diagnosis_code LIKE 'Z59%' THEN 'HOUSING'
            -- Food insecurity (Z59.4, Z59.41, Z59.48)
            WHEN c.diagnosis_code IN ('Z594', 'Z5941', 'Z5948') THEN 'FOOD'
            -- Transportation (Z59.82)
            WHEN c.diagnosis_code = 'Z5982' THEN 'TRANSPORTATION'
            -- Financial strain (Z59.5, Z59.6, Z59.7)
            WHEN c.diagnosis_code IN ('Z595', 'Z596', 'Z597') THEN 'FINANCIAL'
            -- Employment issues (Z56.x)
            WHEN c.diagnosis_code LIKE 'Z56%' THEN 'EMPLOYMENT'
            -- Educational/literacy (Z55.x)
            WHEN c.diagnosis_code LIKE 'Z55%' THEN 'EDUCATION'
            -- Social environment (Z60.x)
            WHEN c.diagnosis_code LIKE 'Z60%' THEN 'SOCIAL_ISOLATION'
            -- Family disruption (Z63.x)
            WHEN c.diagnosis_code LIKE 'Z63%' THEN 'FAMILY_SUPPORT'
            ELSE 'OTHER_SDOH'
        END AS sdoh_category,
        CASE
            WHEN c.diagnosis_code LIKE 'Z59%' THEN 'Housing instability or homelessness'
            WHEN c.diagnosis_code IN ('Z594', 'Z5941', 'Z5948') THEN 'Food insecurity'
            WHEN c.diagnosis_code = 'Z5982' THEN 'Lack of transportation'
            WHEN c.diagnosis_code LIKE 'Z56%' THEN 'Unemployment or work-related stress'
            WHEN c.diagnosis_code LIKE 'Z55%' THEN 'Educational problems or illiteracy'
            ELSE 'Social determinant barrier'
        END AS sdoh_description
    FROM claims c
    WHERE c.diagnosis_code LIKE 'Z5[5-9]%'
       OR c.diagnosis_code LIKE 'Z6[0-5]%'
),
member_sdoh_profile AS (
    SELECT
        member_id,
        COUNT(DISTINCT sdoh_category) AS distinct_sdoh_factors,
        COUNT(*) AS total_sdoh_encounters,
        STRING_AGG(DISTINCT sdoh_category, ', ') AS sdoh_categories,
        MIN(claim_date) AS first_sdoh_documented,
        MAX(claim_date) AS most_recent_sdoh
    FROM sdoh_codes
    GROUP BY member_id
)
SELECT
    msp.member_id,
    msp.distinct_sdoh_factors,
    msp.total_sdoh_encounters,
    msp.sdoh_categories,
    CASE
        WHEN msp.distinct_sdoh_factors >= 3 THEN 'HIGH_RISK'
        WHEN msp.distinct_sdoh_factors = 2 THEN 'MODERATE_RISK'
        WHEN msp.distinct_sdoh_factors = 1 THEN 'SINGLE_BARRIER'
        ELSE 'NO_DOCUMENTED_SDOH'
    END AS sdoh_risk_tier,
    -- Nonadherence odds multiplier based on Berkowitz et al. research
    CASE
        WHEN msp.distinct_sdoh_factors >= 3 THEN 3.26
        WHEN msp.distinct_sdoh_factors = 2 THEN 2.10
        WHEN msp.distinct_sdoh_factors = 1 THEN 1.45
        ELSE 1.00
    END AS expected_nonadherence_multiplier,
    msp.first_sdoh_documented,
    msp.most_recent_sdoh
FROM member_sdoh_profile msp
ORDER BY msp.distinct_sdoh_factors DESC;

-- ============================================================================
-- QUERY 2: Claims-Based SDOH Proxy Signals
-- Infers SDOH barriers from utilization patterns when Z-codes are absent
-- ============================================================================
WITH utilization_signals AS (
    SELECT
        c.member_id,
        -- ED as primary care proxy (access barrier)
        SUM(CASE
            WHEN c.place_of_service = 'ED'
             AND c.primary_diagnosis NOT LIKE 'S%'  -- Not trauma
             AND c.primary_diagnosis NOT LIKE 'T%'  -- Not poisoning
            THEN 1 ELSE 0
        END) AS avoidable_ed_visits,
        -- Prescription abandonment proxy (cost barrier)
        SUM(CASE
            WHEN p.fill_status = 'ABANDONED' THEN 1 ELSE 0
        END) AS abandoned_prescriptions,
        -- Appointment no-shows (transportation/scheduling barrier)
        SUM(CASE
            WHEN a.outcome = 'NO_SHOW' THEN 1 ELSE 0
        END) AS no_shows,
        -- Late-stage ED presentations (delayed care access)
        SUM(CASE
            WHEN c.place_of_service = 'ED'
             AND c.severity_level >= 4
            THEN 1 ELSE 0
        END) AS high_acuity_ed_visits,
        -- After-hours urgent care (work schedule barrier)
        SUM(CASE
            WHEN c.place_of_service = 'URGENT_CARE'
             AND (DATEPART(hour, c.service_time) >= 18 OR DATEPART(hour, c.service_time) <= 7)
            THEN 1 ELSE 0
        END) AS after_hours_visits
    FROM claims c
    LEFT JOIN pharmacy_claims p ON c.member_id = p.member_id
    LEFT JOIN appointments a ON c.member_id = a.member_id
    WHERE c.claim_date >= DATEADD(month, -12, GETDATE())
    GROUP BY c.member_id
),
proxy_sdoh_signals AS (
    SELECT
        member_id,
        avoidable_ed_visits,
        abandoned_prescriptions,
        no_shows,
        high_acuity_ed_visits,
        after_hours_visits,
        -- Score each proxy signal
        CASE WHEN avoidable_ed_visits >= 3 THEN 1 ELSE 0 END AS access_barrier_flag,
        CASE WHEN abandoned_prescriptions >= 2 THEN 1 ELSE 0 END AS cost_barrier_flag,
        CASE WHEN no_shows >= 3 THEN 1 ELSE 0 END AS scheduling_barrier_flag,
        CASE WHEN high_acuity_ed_visits >= 2 THEN 1 ELSE 0 END AS delayed_care_flag,
        CASE WHEN after_hours_visits >= 3 THEN 1 ELSE 0 END AS work_conflict_flag
    FROM utilization_signals
)
SELECT
    pss.member_id,
    pss.access_barrier_flag + pss.cost_barrier_flag + pss.scheduling_barrier_flag
        + pss.delayed_care_flag + pss.work_conflict_flag AS proxy_sdoh_score,
    CASE WHEN pss.access_barrier_flag = 1 THEN 'ACCESS_BARRIER' ELSE NULL END AS barrier_1,
    CASE WHEN pss.cost_barrier_flag = 1 THEN 'COST_BARRIER' ELSE NULL END AS barrier_2,
    CASE WHEN pss.scheduling_barrier_flag = 1 THEN 'SCHEDULING_BARRIER' ELSE NULL END AS barrier_3,
    CASE WHEN pss.delayed_care_flag = 1 THEN 'DELAYED_CARE' ELSE NULL END AS barrier_4,
    CASE WHEN pss.work_conflict_flag = 1 THEN 'WORK_CONFLICT' ELSE NULL END AS barrier_5,
    CASE
        WHEN pss.access_barrier_flag + pss.cost_barrier_flag + pss.scheduling_barrier_flag
             + pss.delayed_care_flag + pss.work_conflict_flag >= 3 THEN 'MULTI_BARRIER'
        WHEN pss.access_barrier_flag + pss.cost_barrier_flag + pss.scheduling_barrier_flag
             + pss.delayed_care_flag + pss.work_conflict_flag >= 1 THEN 'SINGLE_BARRIER'
        ELSE 'NO_PROXY_SIGNALS'
    END AS proxy_sdoh_tier,
    pss.avoidable_ed_visits,
    pss.abandoned_prescriptions,
    pss.no_shows
FROM proxy_sdoh_signals pss
WHERE pss.access_barrier_flag + pss.cost_barrier_flag + pss.scheduling_barrier_flag
      + pss.delayed_care_flag + pss.work_conflict_flag >= 1
ORDER BY pss.access_barrier_flag + pss.cost_barrier_flag + pss.scheduling_barrier_flag
         + pss.delayed_care_flag + pss.work_conflict_flag DESC;

-- ============================================================================
-- QUERY 3: SDOH Cluster Definition for Intervention Matching
-- Groups members into actionable clusters based on dominant SDOH pattern
-- ============================================================================
WITH combined_sdoh AS (
    -- Combine Z-code documented SDOH with proxy signals
    SELECT
        COALESCE(z.member_id, p.member_id) AS member_id,
        z.sdoh_categories AS documented_sdoh,
        z.distinct_sdoh_factors AS documented_count,
        p.proxy_sdoh_score,
        p.barrier_1, p.barrier_2, p.barrier_3, p.barrier_4, p.barrier_5
    FROM (
        SELECT member_id, STRING_AGG(DISTINCT sdoh_category, ', ') AS sdoh_categories,
               COUNT(DISTINCT sdoh_category) AS distinct_sdoh_factors
        FROM (
            SELECT member_id,
                   CASE WHEN diagnosis_code LIKE 'Z59%' THEN 'HOUSING'
                        WHEN diagnosis_code LIKE 'Z56%' THEN 'EMPLOYMENT'
                        WHEN diagnosis_code LIKE 'Z55%' THEN 'EDUCATION'
                        WHEN diagnosis_code LIKE 'Z60%' THEN 'SOCIAL'
                        ELSE 'OTHER' END AS sdoh_category
            FROM claims WHERE diagnosis_code LIKE 'Z5[5-9]%' OR diagnosis_code LIKE 'Z6[0-5]%'
        ) zc GROUP BY member_id
    ) z
    FULL OUTER JOIN (
        SELECT member_id,
               access_barrier_flag + cost_barrier_flag + scheduling_barrier_flag AS proxy_sdoh_score,
               CASE WHEN access_barrier_flag = 1 THEN 'ACCESS' END AS barrier_1,
               CASE WHEN cost_barrier_flag = 1 THEN 'COST' END AS barrier_2,
               CASE WHEN scheduling_barrier_flag = 1 THEN 'SCHEDULING' END AS barrier_3,
               CASE WHEN delayed_care_flag = 1 THEN 'DELAYED' END AS barrier_4,
               CASE WHEN work_conflict_flag = 1 THEN 'WORK' END AS barrier_5
        FROM (
            SELECT member_id,
                   CASE WHEN COUNT(CASE WHEN place_of_service = 'ED' THEN 1 END) >= 3 THEN 1 ELSE 0 END AS access_barrier_flag,
                   CASE WHEN COUNT(CASE WHEN fill_status = 'ABANDONED' THEN 1 END) >= 2 THEN 1 ELSE 0 END AS cost_barrier_flag,
                   CASE WHEN COUNT(CASE WHEN outcome = 'NO_SHOW' THEN 1 END) >= 3 THEN 1 ELSE 0 END AS scheduling_barrier_flag,
                   0 AS delayed_care_flag, 0 AS work_conflict_flag
            FROM claims c
            LEFT JOIN pharmacy_claims p ON c.member_id = p.member_id
            LEFT JOIN appointments a ON c.member_id = a.member_id
            GROUP BY member_id
        ) sub
    ) p ON z.member_id = p.member_id
)
SELECT
    member_id,
    -- Assign to intervention cluster based on dominant barrier pattern
    CASE
        WHEN documented_sdoh LIKE '%HOUSING%' THEN 'HOUSING_FIRST'
        WHEN documented_sdoh LIKE '%FOOD%' OR barrier_2 = 'COST' THEN 'FOOD_RX_ELIGIBLE'
        WHEN documented_sdoh LIKE '%TRANSPORTATION%' OR barrier_3 = 'SCHEDULING' THEN 'TRANSPORTATION_SUPPORT'
        WHEN barrier_1 = 'ACCESS' THEN 'NETWORK_NAVIGATION'
        WHEN documented_sdoh LIKE '%EMPLOYMENT%' OR barrier_5 = 'WORK' THEN 'FLEXIBLE_SCHEDULING'
        WHEN COALESCE(documented_count, 0) + COALESCE(proxy_sdoh_score, 0) >= 3 THEN 'COMPLEX_INTERVENTION'
        ELSE 'STANDARD_CARE_MANAGEMENT'
    END AS intervention_cluster,
    CASE
        WHEN documented_sdoh LIKE '%HOUSING%' THEN 'Refer to housing partnership program'
        WHEN documented_sdoh LIKE '%FOOD%' OR barrier_2 = 'COST' THEN 'Enroll in food pharmacy or cost assistance'
        WHEN documented_sdoh LIKE '%TRANSPORTATION%' THEN 'Activate escorted transport (not app-based)'
        WHEN barrier_1 = 'ACCESS' THEN 'Connect with patient navigator for network access'
        ELSE 'Standard care management with SDOH awareness'
    END AS recommended_intervention,
    COALESCE(documented_count, 0) + COALESCE(proxy_sdoh_score, 0) AS combined_sdoh_score,
    documented_sdoh,
    proxy_sdoh_score
FROM combined_sdoh
ORDER BY COALESCE(documented_count, 0) + COALESCE(proxy_sdoh_score, 0) DESC;

-- ============================================================================
-- QUERY 4: Intervention Capacity Matching
-- Ensures we don't flag members for interventions we can't actually provide
-- ============================================================================
WITH intervention_capacity AS (
    -- This should be populated from your actual intervention inventory
    SELECT 'HOUSING_FIRST' AS cluster, 50 AS monthly_capacity, 'Active' AS status UNION ALL
    SELECT 'FOOD_RX_ELIGIBLE', 200, 'Active' UNION ALL
    SELECT 'TRANSPORTATION_SUPPORT', 500, 'Active' UNION ALL
    SELECT 'NETWORK_NAVIGATION', 300, 'Active' UNION ALL
    SELECT 'FLEXIBLE_SCHEDULING', 100, 'Pilot' UNION ALL
    SELECT 'COMPLEX_INTERVENTION', 25, 'Limited'
),
member_clusters AS (
    -- Use results from Query 3
    SELECT
        member_id,
        'HOUSING_FIRST' AS intervention_cluster -- Simplified; use actual cluster logic
    FROM members
    WHERE member_id IN (SELECT member_id FROM claims WHERE diagnosis_code LIKE 'Z59%')
),
cluster_demand AS (
    SELECT
        mc.intervention_cluster,
        COUNT(*) AS members_in_cluster
    FROM member_clusters mc
    GROUP BY mc.intervention_cluster
)
SELECT
    cd.intervention_cluster,
    cd.members_in_cluster AS demand,
    ic.monthly_capacity AS capacity,
    cd.members_in_cluster - ic.monthly_capacity AS gap,
    CASE
        WHEN cd.members_in_cluster <= ic.monthly_capacity THEN 'CAPACITY_AVAILABLE'
        WHEN ic.monthly_capacity > 0 THEN 'CAPACITY_CONSTRAINED'
        ELSE 'NO_INTERVENTION_AVAILABLE'
    END AS intervention_status,
    CASE
        WHEN cd.members_in_cluster > ic.monthly_capacity
        THEN 'Flag ' || ic.monthly_capacity || ' of ' || cd.members_in_cluster || ' - prioritize by clinical acuity'
        ELSE 'All members can receive intervention'
    END AS operational_guidance
FROM cluster_demand cd
LEFT JOIN intervention_capacity ic ON cd.intervention_cluster = ic.cluster
ORDER BY cd.members_in_cluster - COALESCE(ic.monthly_capacity, 0) DESC;

-- ============================================================================
-- QUERY 5: SDOH-Adjusted Risk Score Recalibration
-- Based on Obermeyer et al.: cost-based risk scores under-identify marginalized populations
-- ============================================================================
WITH current_risk_scores AS (
    SELECT
        r.member_id,
        r.risk_score,
        r.risk_percentile,
        r.predicted_cost,
        r.algorithm_version
    FROM risk_stratification r
    WHERE r.score_date = (SELECT MAX(score_date) FROM risk_stratification)
),
clinical_need_indicators AS (
    SELECT
        c.member_id,
        COUNT(DISTINCT c.chronic_condition_code) AS chronic_condition_count,
        SUM(CASE WHEN c.primary_diagnosis LIKE 'E11%' THEN 1 ELSE 0 END) AS diabetes_indicators,
        SUM(CASE WHEN c.primary_diagnosis LIKE 'I10%' THEN 1 ELSE 0 END) AS hypertension_indicators,
        AVG(CASE WHEN l.result_value IS NOT NULL THEN l.result_value END) AS avg_hba1c,
        COUNT(DISTINCT CASE WHEN c.place_of_service = 'ED' THEN c.claim_id END) AS ed_visits
    FROM claims c
    LEFT JOIN lab_results l ON c.member_id = l.member_id AND l.test_type = 'HBA1C'
    WHERE c.claim_date >= DATEADD(month, -12, GETDATE())
    GROUP BY c.member_id
),
sdoh_burden AS (
    SELECT
        member_id,
        COUNT(DISTINCT sdoh_category) AS sdoh_factor_count
    FROM (
        SELECT member_id,
               CASE WHEN diagnosis_code LIKE 'Z59%' THEN 'HOUSING'
                    WHEN diagnosis_code LIKE 'Z56%' THEN 'EMPLOYMENT'
                    ELSE 'OTHER' END AS sdoh_category
        FROM claims WHERE diagnosis_code LIKE 'Z5[5-9]%'
    ) z
    GROUP BY member_id
)
SELECT
    crs.member_id,
    crs.risk_score AS original_risk_score,
    crs.risk_percentile AS original_percentile,
    cni.chronic_condition_count,
    sb.sdoh_factor_count,
    -- Clinical need adjustment (independent of cost utilization)
    CASE
        WHEN cni.chronic_condition_count >= 5 AND crs.risk_percentile < 80 THEN 'UNDER_IDENTIFIED'
        WHEN cni.avg_hba1c > 9.0 AND crs.risk_percentile < 70 THEN 'UNDER_IDENTIFIED'
        WHEN sb.sdoh_factor_count >= 2 AND crs.risk_percentile < 75 THEN 'UNDER_IDENTIFIED'
        ELSE 'APPROPRIATELY_SCORED'
    END AS bias_flag,
    -- Adjusted percentile based on clinical need
    CASE
        WHEN cni.chronic_condition_count >= 5 THEN GREATEST(crs.risk_percentile, 85)
        WHEN cni.avg_hba1c > 9.0 THEN GREATEST(crs.risk_percentile, 80)
        WHEN sb.sdoh_factor_count >= 2 THEN GREATEST(crs.risk_percentile, 75)
        ELSE crs.risk_percentile
    END AS adjusted_percentile,
    'See Obermeyer et al. 2019 Science for methodology' AS methodology_note
FROM current_risk_scores crs
LEFT JOIN clinical_need_indicators cni ON crs.member_id = cni.member_id
LEFT JOIN sdoh_burden sb ON crs.member_id = sb.member_id
WHERE cni.chronic_condition_count >= 3 OR sb.sdoh_factor_count >= 1
ORDER BY
    CASE WHEN cni.chronic_condition_count >= 5 AND crs.risk_percentile < 80 THEN 1
         WHEN sb.sdoh_factor_count >= 2 AND crs.risk_percentile < 75 THEN 2
         ELSE 3 END,
    cni.chronic_condition_count DESC;
