-- Vendor Performance Scorecard SQL Templates
-- Vitals & Variables Edition 18: Care Management AI vs. Member Reality
--
-- These queries measure vendor performance against member outcomes,
-- not just SLA compliance. A vendor can hit every SLA and still fail
-- if members don't improve.
--
-- Key insight: If your intervention vendor's success metric is
-- "outreach attempted," you're documenting failure at scale.

-- ============================================================================
-- QUERY 1: Transportation Vendor Effectiveness
-- Based on Chaiyachati et al. (2018): free rideshare had NO effect on
-- no-show rates (36.5% vs 36.7%, p=0.96). Only 25% of offered rides were used.
-- ============================================================================
WITH transport_rides AS (
    SELECT
        tv.vendor_name,
        tv.ride_id,
        tv.member_id,
        tv.scheduled_pickup_time,
        tv.actual_pickup_time,
        tv.ride_status, -- 'COMPLETED', 'NO_SHOW', 'CANCELLED', 'DRIVER_NO_SHOW'
        tv.ride_type,   -- 'APP_BASED', 'ESCORTED', 'NEMT'
        tv.associated_appointment_id
    FROM transportation_vendor_log tv
    WHERE tv.scheduled_pickup_time >= DATEADD(month, -6, GETDATE())
),
ride_outcomes AS (
    SELECT
        tr.vendor_name,
        tr.ride_type,
        COUNT(*) AS total_rides_scheduled,
        SUM(CASE WHEN tr.ride_status = 'COMPLETED' THEN 1 ELSE 0 END) AS rides_completed,
        SUM(CASE WHEN tr.ride_status = 'NO_SHOW' THEN 1 ELSE 0 END) AS member_no_shows,
        SUM(CASE WHEN tr.ride_status = 'DRIVER_NO_SHOW' THEN 1 ELSE 0 END) AS driver_no_shows,
        SUM(CASE WHEN tr.ride_status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancellations
    FROM transport_rides tr
    GROUP BY tr.vendor_name, tr.ride_type
),
appointment_outcomes AS (
    SELECT
        tr.vendor_name,
        tr.ride_type,
        COUNT(DISTINCT tr.member_id) AS members_served,
        SUM(CASE WHEN a.outcome = 'COMPLETED' THEN 1 ELSE 0 END) AS appointments_kept,
        SUM(CASE WHEN a.outcome = 'NO_SHOW' THEN 1 ELSE 0 END) AS appointments_missed
    FROM transport_rides tr
    LEFT JOIN appointments a ON tr.associated_appointment_id = a.appointment_id
    WHERE tr.ride_status = 'COMPLETED'
    GROUP BY tr.vendor_name, tr.ride_type
)
SELECT
    ro.vendor_name,
    ro.ride_type,
    ro.total_rides_scheduled,
    ro.rides_completed,
    ROUND(100.0 * ro.rides_completed / NULLIF(ro.total_rides_scheduled, 0), 1) AS ride_completion_rate,
    ro.driver_no_shows,
    ao.appointments_kept,
    ao.appointments_missed,
    -- THE REAL METRIC: Did the ride result in care?
    ROUND(100.0 * ao.appointments_kept / NULLIF(ao.appointments_kept + ao.appointments_missed, 0), 1) AS care_delivery_rate,
    CASE
        WHEN 100.0 * ao.appointments_kept / NULLIF(ao.appointments_kept + ao.appointments_missed, 0) >= 80 THEN 'EFFECTIVE'
        WHEN 100.0 * ao.appointments_kept / NULLIF(ao.appointments_kept + ao.appointments_missed, 0) >= 60 THEN 'MARGINAL'
        ELSE 'INEFFECTIVE'
    END AS vendor_effectiveness,
    CASE
        WHEN ro.ride_type = 'APP_BASED' AND ao.appointments_missed > ao.appointments_kept
        THEN 'Consider: App-based rides may not suit this population (Chaiyachati 2018)'
        WHEN ro.driver_no_shows > ro.total_rides_scheduled * 0.1
        THEN 'Driver reliability issue - review vendor contract'
        ELSE 'Monitor performance'
    END AS recommendation
FROM ride_outcomes ro
LEFT JOIN appointment_outcomes ao ON ro.vendor_name = ao.vendor_name AND ro.ride_type = ao.ride_type
ORDER BY care_delivery_rate ASC;

-- ============================================================================
-- QUERY 2: Care Management Vendor Outreach Effectiveness
-- Measures outcome impact, not just "touches"
-- ============================================================================
WITH vendor_outreach AS (
    SELECT
        cmv.vendor_name,
        cmv.member_id,
        cmv.outreach_date,
        cmv.outreach_type,   -- 'PHONE', 'SMS', 'HOME_VISIT', 'MAIL'
        cmv.outcome,         -- 'REACHED', 'VOICEMAIL', 'NO_ANSWER', 'ENGAGED'
        cmv.care_gap_id
    FROM care_management_vendor_log cmv
    WHERE cmv.outreach_date >= DATEADD(month, -6, GETDATE())
),
vendor_metrics AS (
    SELECT
        vendor_name,
        COUNT(DISTINCT member_id) AS members_assigned,
        COUNT(*) AS total_outreach_attempts,
        SUM(CASE WHEN outcome IN ('REACHED', 'ENGAGED') THEN 1 ELSE 0 END) AS successful_contacts,
        SUM(CASE WHEN outcome = 'ENGAGED' THEN 1 ELSE 0 END) AS engaged_contacts,
        COUNT(DISTINCT care_gap_id) AS care_gaps_addressed
    FROM vendor_outreach
    GROUP BY vendor_name
),
care_gap_closure AS (
    SELECT
        vo.vendor_name,
        COUNT(DISTINCT cg.care_gap_id) AS gaps_closed,
        AVG(DATEDIFF(day, vo.outreach_date, cg.closure_date)) AS avg_days_to_closure
    FROM vendor_outreach vo
    INNER JOIN care_management_gaps cg ON vo.care_gap_id = cg.care_gap_id
    WHERE cg.status = 'CLOSED'
    GROUP BY vo.vendor_name
),
clinical_outcomes AS (
    SELECT
        vo.vendor_name,
        -- 30-day readmission rate for members touched by vendor
        AVG(CASE WHEN adm.readmission_30day = 1 THEN 1.0 ELSE 0.0 END) AS readmission_rate,
        -- ED utilization trend
        AVG(co.ed_visits_post) - AVG(co.ed_visits_pre) AS ed_visit_delta
    FROM vendor_outreach vo
    LEFT JOIN admissions adm ON vo.member_id = adm.member_id
        AND adm.admission_date BETWEEN vo.outreach_date AND DATEADD(day, 60, vo.outreach_date)
    LEFT JOIN (
        SELECT
            member_id,
            SUM(CASE WHEN claim_date < DATEADD(month, -6, GETDATE()) THEN 1 ELSE 0 END) AS ed_visits_pre,
            SUM(CASE WHEN claim_date >= DATEADD(month, -6, GETDATE()) THEN 1 ELSE 0 END) AS ed_visits_post
        FROM claims
        WHERE place_of_service = 'ED'
        GROUP BY member_id
    ) co ON vo.member_id = co.member_id
    GROUP BY vo.vendor_name
)
SELECT
    vm.vendor_name,
    vm.members_assigned,
    vm.total_outreach_attempts,
    ROUND(1.0 * vm.total_outreach_attempts / NULLIF(vm.members_assigned, 0), 1) AS attempts_per_member,
    ROUND(100.0 * vm.successful_contacts / NULLIF(vm.total_outreach_attempts, 0), 1) AS contact_rate,
    ROUND(100.0 * vm.engaged_contacts / NULLIF(vm.successful_contacts, 0), 1) AS engagement_rate,
    cgc.gaps_closed,
    ROUND(100.0 * cgc.gaps_closed / NULLIF(vm.care_gaps_addressed, 0), 1) AS gap_closure_rate,
    cgc.avg_days_to_closure,
    ROUND(100.0 * co.readmission_rate, 1) AS readmission_rate_pct,
    co.ed_visit_delta,
    -- Overall vendor grade
    CASE
        WHEN cgc.gaps_closed * 1.0 / NULLIF(vm.care_gaps_addressed, 0) >= 0.5
         AND co.ed_visit_delta <= 0
        THEN 'A - EFFECTIVE'
        WHEN cgc.gaps_closed * 1.0 / NULLIF(vm.care_gaps_addressed, 0) >= 0.3
        THEN 'B - MODERATE'
        WHEN vm.successful_contacts * 1.0 / NULLIF(vm.total_outreach_attempts, 0) >= 0.5
        THEN 'C - PROCESS COMPLIANT'
        ELSE 'D - INEFFECTIVE'
    END AS vendor_grade,
    CASE
        WHEN cgc.gaps_closed * 1.0 / NULLIF(vm.care_gaps_addressed, 0) < 0.2
        THEN 'High outreach volume with low outcome impact - review intervention design'
        WHEN vm.total_outreach_attempts / NULLIF(vm.members_assigned, 0) > 10
         AND cgc.gaps_closed * 1.0 / NULLIF(vm.care_gaps_addressed, 0) < 0.3
        THEN 'Repeated outreach to members with system friction - review member stratification'
        ELSE 'Continue monitoring'
    END AS performance_note
FROM vendor_metrics vm
LEFT JOIN care_gap_closure cgc ON vm.vendor_name = cgc.vendor_name
LEFT JOIN clinical_outcomes co ON vm.vendor_name = co.vendor_name
ORDER BY cgc.gaps_closed * 1.0 / NULLIF(vm.care_gaps_addressed, 0) DESC;

-- ============================================================================
-- QUERY 3: Pharmacy Benefit Manager (PBM) Friction Contribution
-- Measures PBM's role in creating adherence barriers
-- ============================================================================
WITH pbm_performance AS (
    SELECT
        pbm.pbm_name,
        rx.member_id,
        rx.drug_class,
        rx.fill_status,
        rx.member_oop_cost,
        rx.formulary_tier,
        rx.step_therapy_required,
        rx.prior_auth_required,
        CASE WHEN rx.fill_status = 'ABANDONED' THEN 1 ELSE 0 END AS was_abandoned
    FROM pharmacy_claims rx
    INNER JOIN pbm_contracts pbm ON rx.pbm_id = pbm.pbm_id
    WHERE rx.fill_date >= DATEADD(month, -12, GETDATE())
),
pbm_metrics AS (
    SELECT
        pbm_name,
        COUNT(*) AS total_fills,
        AVG(member_oop_cost) AS avg_member_oop,
        SUM(was_abandoned) AS abandoned_fills,
        SUM(CASE WHEN step_therapy_required = 1 THEN 1 ELSE 0 END) AS step_therapy_count,
        SUM(CASE WHEN prior_auth_required = 1 THEN 1 ELSE 0 END) AS pa_required_count,
        SUM(CASE WHEN formulary_tier >= 3 THEN 1 ELSE 0 END) AS high_tier_fills
    FROM pbm_performance
    GROUP BY pbm_name
),
pbm_adherence_impact AS (
    SELECT
        pp.pbm_name,
        AVG(CASE WHEN am.pdc_score >= 0.8 THEN 1.0 ELSE 0.0 END) AS adherent_rate,
        AVG(am.pdc_score) AS avg_pdc
    FROM pbm_performance pp
    LEFT JOIN adherence_metrics am ON pp.member_id = am.member_id AND pp.drug_class = am.drug_class
    GROUP BY pp.pbm_name
)
SELECT
    pm.pbm_name,
    pm.total_fills,
    ROUND(pm.avg_member_oop, 2) AS avg_member_oop,
    ROUND(100.0 * pm.abandoned_fills / NULLIF(pm.total_fills, 0), 1) AS abandonment_rate,
    ROUND(100.0 * pm.pa_required_count / NULLIF(pm.total_fills, 0), 1) AS pa_burden_rate,
    ROUND(100.0 * pm.step_therapy_count / NULLIF(pm.total_fills, 0), 1) AS step_therapy_rate,
    ROUND(100.0 * pai.adherent_rate, 1) AS pdc_adherent_rate,
    CASE
        WHEN pm.avg_member_oop > 75 AND pm.abandoned_fills * 1.0 / pm.total_fills > 0.15
        THEN 'HIGH FRICTION'
        WHEN pm.pa_required_count * 1.0 / pm.total_fills > 0.3
        THEN 'PA BURDEN'
        WHEN pai.avg_pdc < 0.7
        THEN 'ADHERENCE CONCERN'
        ELSE 'ACCEPTABLE'
    END AS pbm_friction_level,
    CASE
        WHEN pm.avg_member_oop > 100
        THEN 'Cost-sharing design driving abandonment (Eaddy et al. 2012)'
        WHEN pm.pa_required_count * 1.0 / pm.total_fills > 0.4
        THEN 'Excessive PA burden - review gold-carding eligibility'
        ELSE 'Monitor trends'
    END AS recommendation
FROM pbm_metrics pm
LEFT JOIN pbm_adherence_impact pai ON pm.pbm_name = pai.pbm_name
ORDER BY pm.abandoned_fills * 1.0 / NULLIF(pm.total_fills, 0) DESC;

-- ============================================================================
-- QUERY 4: Composite Vendor Scorecard Summary
-- Aggregated view for executive reporting
-- ============================================================================
WITH all_vendors AS (
    SELECT 'Transportation' AS vendor_type, vendor_name,
           rides_completed * 1.0 / NULLIF(total_rides_scheduled, 0) AS completion_rate,
           appointments_kept * 1.0 / NULLIF(appointments_kept + appointments_missed, 0) AS outcome_rate
    FROM (
        SELECT vendor_name,
               COUNT(*) AS total_rides_scheduled,
               SUM(CASE WHEN ride_status = 'COMPLETED' THEN 1 ELSE 0 END) AS rides_completed,
               0 AS appointments_kept, 0 AS appointments_missed
        FROM transportation_vendor_log
        WHERE scheduled_pickup_time >= DATEADD(month, -6, GETDATE())
        GROUP BY vendor_name
    ) t
    UNION ALL
    SELECT 'Care Management' AS vendor_type, vendor_name,
           successful_contacts * 1.0 / NULLIF(total_outreach, 0) AS completion_rate,
           gaps_closed * 1.0 / NULLIF(gaps_addressed, 0) AS outcome_rate
    FROM (
        SELECT vendor_name,
               COUNT(*) AS total_outreach,
               SUM(CASE WHEN outcome IN ('REACHED', 'ENGAGED') THEN 1 ELSE 0 END) AS successful_contacts,
               COUNT(DISTINCT care_gap_id) AS gaps_addressed,
               SUM(CASE WHEN gap_status = 'CLOSED' THEN 1 ELSE 0 END) AS gaps_closed
        FROM care_management_vendor_log cmv
        LEFT JOIN care_management_gaps cg ON cmv.care_gap_id = cg.care_gap_id
        WHERE outreach_date >= DATEADD(month, -6, GETDATE())
        GROUP BY vendor_name
    ) cm
)
SELECT
    vendor_type,
    vendor_name,
    ROUND(100.0 * completion_rate, 1) AS process_completion_pct,
    ROUND(100.0 * outcome_rate, 1) AS outcome_success_pct,
    CASE
        WHEN outcome_rate >= 0.6 THEN 'GREEN'
        WHEN outcome_rate >= 0.4 THEN 'YELLOW'
        ELSE 'RED'
    END AS status,
    CASE
        WHEN completion_rate >= 0.8 AND outcome_rate < 0.4
        THEN 'High activity, low impact - intervention design issue'
        WHEN completion_rate < 0.5
        THEN 'Operational execution issue'
        ELSE 'Review periodically'
    END AS insight
FROM all_vendors
ORDER BY vendor_type, outcome_rate DESC;
