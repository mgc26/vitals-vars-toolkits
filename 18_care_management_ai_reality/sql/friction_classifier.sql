-- Care Management Friction Classifier SQL Templates
-- Vitals & Variables Edition 18: Care Management AI vs. Member Reality
--
-- These queries help identify where SYSTEM friction—not member behavior—
-- drives apparent nonadherence. Use these to shift from blaming members
-- to interrogating your own operations.
--
-- Compatible with: SQL Server, PostgreSQL, Oracle (with minor syntax adjustments)
-- Required tables: claims, pharmacy, authorizations, outreach_log, member_demographics

-- ============================================================================
-- QUERY 1: Prior Authorization Delay Impact
-- Identifies members whose treatment was delayed by PA processes
-- ============================================================================
WITH pa_delays AS (
    SELECT
        a.member_id,
        a.auth_request_date,
        a.auth_approval_date,
        a.service_type,
        a.procedure_code,
        DATEDIFF(day, a.auth_request_date, a.auth_approval_date) AS days_to_approval,
        CASE
            WHEN a.required_peer_review = 1 THEN 'Peer-to-Peer Required'
            WHEN a.required_appeal = 1 THEN 'Appeal Required'
            WHEN a.auto_approved = 1 THEN 'Auto-Approved'
            ELSE 'Standard Review'
        END AS approval_pathway,
        a.outcome -- 'APPROVED', 'DENIED', 'WITHDRAWN'
    FROM authorizations a
    WHERE a.auth_request_date >= DATEADD(month, -12, GETDATE())
),
member_pa_burden AS (
    SELECT
        member_id,
        COUNT(*) AS total_pa_requests,
        SUM(CASE WHEN outcome = 'DENIED' THEN 1 ELSE 0 END) AS denials,
        AVG(days_to_approval) AS avg_days_to_approval,
        SUM(CASE WHEN days_to_approval > 14 THEN 1 ELSE 0 END) AS delayed_auths,
        SUM(CASE WHEN approval_pathway = 'Peer-to-Peer Required' THEN 1 ELSE 0 END) AS p2p_required
    FROM pa_delays
    WHERE outcome = 'APPROVED'
    GROUP BY member_id
)
SELECT
    mpb.member_id,
    mpb.total_pa_requests,
    mpb.denials,
    mpb.avg_days_to_approval,
    mpb.delayed_auths,
    mpb.p2p_required,
    CASE
        WHEN mpb.avg_days_to_approval > 14 THEN 'HIGH'
        WHEN mpb.avg_days_to_approval > 7 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS pa_friction_level,
    'PA_DELAY' AS friction_type
FROM member_pa_burden mpb
WHERE mpb.avg_days_to_approval > 7 OR mpb.denials > 0;

-- ============================================================================
-- QUERY 2: Cost-Sharing Abandonment Analysis
-- Identifies prescriptions abandoned due to high out-of-pocket costs
-- Based on Eaddy et al. finding: $10 OOP increase = 1.9% adherence drop
-- ============================================================================
WITH rx_attempts AS (
    SELECT
        p.member_id,
        p.fill_date,
        p.drug_name,
        p.drug_class,
        p.member_oop_cost,
        p.fill_status, -- 'FILLED', 'ABANDONED', 'PARTIAL'
        p.days_supply,
        p.is_specialty_drug,
        LAG(p.member_oop_cost) OVER (
            PARTITION BY p.member_id, p.drug_class
            ORDER BY p.fill_date
        ) AS prior_oop_cost
    FROM pharmacy_claims p
    WHERE p.fill_date >= DATEADD(month, -12, GETDATE())
),
abandonment_patterns AS (
    SELECT
        member_id,
        drug_class,
        COUNT(*) AS total_attempts,
        SUM(CASE WHEN fill_status = 'ABANDONED' THEN 1 ELSE 0 END) AS abandoned_fills,
        AVG(member_oop_cost) AS avg_oop_cost,
        MAX(member_oop_cost) AS max_oop_cost,
        SUM(CASE WHEN member_oop_cost > 100 THEN 1 ELSE 0 END) AS high_cost_fills,
        SUM(CASE WHEN is_specialty_drug = 1 AND fill_status = 'ABANDONED' THEN 1 ELSE 0 END) AS specialty_abandons
    FROM rx_attempts
    GROUP BY member_id, drug_class
)
SELECT
    ap.member_id,
    ap.drug_class,
    ap.total_attempts,
    ap.abandoned_fills,
    ROUND(100.0 * ap.abandoned_fills / NULLIF(ap.total_attempts, 0), 1) AS abandonment_rate,
    ap.avg_oop_cost,
    ap.max_oop_cost,
    CASE
        WHEN ap.avg_oop_cost > 100 THEN 'HIGH'
        WHEN ap.avg_oop_cost > 50 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS cost_friction_level,
    'COST_BARRIER' AS friction_type
FROM abandonment_patterns ap
WHERE ap.abandoned_fills > 0 OR ap.avg_oop_cost > 50;

-- ============================================================================
-- QUERY 3: Network Adequacy Gaps
-- Identifies members whose nonadherence may stem from network access issues
-- ============================================================================
WITH member_pcp_distance AS (
    SELECT
        m.member_id,
        m.zip_code AS member_zip,
        p.provider_id,
        p.zip_code AS provider_zip,
        p.specialty,
        p.accepting_new_patients,
        -- Simplified distance calculation (use actual geo functions in production)
        ABS(CAST(LEFT(m.zip_code, 3) AS INT) - CAST(LEFT(p.zip_code, 3) AS INT)) AS zip_distance_proxy
    FROM members m
    CROSS APPLY (
        SELECT TOP 3 *
        FROM providers p
        WHERE p.specialty = 'PRIMARY_CARE'
          AND p.network_status = 'IN_NETWORK'
          AND p.accepting_new_patients = 1
        ORDER BY ABS(CAST(LEFT(m.zip_code, 3) AS INT) - CAST(LEFT(p.zip_code, 3) AS INT))
    ) p
),
appointment_availability AS (
    SELECT
        a.member_id,
        a.requested_date,
        a.scheduled_date,
        DATEDIFF(day, a.requested_date, a.scheduled_date) AS days_until_available,
        a.appointment_type,
        a.outcome -- 'COMPLETED', 'NO_SHOW', 'CANCELLED'
    FROM appointments a
    WHERE a.requested_date >= DATEADD(month, -6, GETDATE())
)
SELECT
    m.member_id,
    MIN(mpd.zip_distance_proxy) AS nearest_pcp_distance_proxy,
    COUNT(DISTINCT aa.appointment_type) AS appointment_types_scheduled,
    AVG(aa.days_until_available) AS avg_wait_days,
    SUM(CASE WHEN aa.outcome = 'NO_SHOW' THEN 1 ELSE 0 END) AS no_shows,
    SUM(CASE WHEN aa.outcome = 'CANCELLED' THEN 1 ELSE 0 END) AS cancellations,
    CASE
        WHEN AVG(aa.days_until_available) > 21 THEN 'HIGH'
        WHEN AVG(aa.days_until_available) > 14 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS access_friction_level,
    'NETWORK_ACCESS' AS friction_type
FROM members m
LEFT JOIN member_pcp_distance mpd ON m.member_id = mpd.member_id
LEFT JOIN appointment_availability aa ON m.member_id = aa.member_id
GROUP BY m.member_id
HAVING AVG(aa.days_until_available) > 14 OR MIN(mpd.zip_distance_proxy) > 10;

-- ============================================================================
-- QUERY 4: Outreach Timing Mismatch Analysis
-- Identifies members contacted during work hours who may not be able to respond
-- ============================================================================
WITH outreach_patterns AS (
    SELECT
        o.member_id,
        o.outreach_date,
        o.outreach_time,
        DATEPART(hour, o.outreach_time) AS outreach_hour,
        DATEPART(weekday, o.outreach_date) AS outreach_dow,
        o.channel, -- 'PHONE', 'SMS', 'EMAIL', 'MAIL'
        o.outcome, -- 'REACHED', 'VOICEMAIL', 'NO_ANSWER', 'WRONG_NUMBER'
        o.campaign_type
    FROM outreach_log o
    WHERE o.outreach_date >= DATEADD(month, -6, GETDATE())
),
member_reachability AS (
    SELECT
        member_id,
        COUNT(*) AS total_attempts,
        SUM(CASE WHEN outcome = 'REACHED' THEN 1 ELSE 0 END) AS successful_contacts,
        SUM(CASE WHEN outcome IN ('NO_ANSWER', 'VOICEMAIL') THEN 1 ELSE 0 END) AS missed_contacts,
        -- Work hour attempts (9am-5pm weekdays)
        SUM(CASE
            WHEN outreach_hour BETWEEN 9 AND 17
             AND outreach_dow BETWEEN 2 AND 6
             AND outcome IN ('NO_ANSWER', 'VOICEMAIL')
            THEN 1 ELSE 0
        END) AS work_hour_misses,
        -- Evening/weekend attempts
        SUM(CASE
            WHEN (outreach_hour < 9 OR outreach_hour > 17 OR outreach_dow IN (1, 7))
             AND outcome = 'REACHED'
            THEN 1 ELSE 0
        END) AS off_hour_successes
    FROM outreach_patterns
    GROUP BY member_id
)
SELECT
    mr.member_id,
    mr.total_attempts,
    mr.successful_contacts,
    ROUND(100.0 * mr.successful_contacts / NULLIF(mr.total_attempts, 0), 1) AS contact_rate,
    mr.work_hour_misses,
    mr.off_hour_successes,
    CASE
        WHEN mr.work_hour_misses > 3 AND mr.successful_contacts = 0 THEN 'HIGH'
        WHEN mr.work_hour_misses > 1 AND mr.successful_contacts < 2 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS timing_friction_level,
    'OUTREACH_TIMING' AS friction_type
FROM member_reachability mr
WHERE mr.total_attempts > 2
  AND ROUND(100.0 * mr.successful_contacts / NULLIF(mr.total_attempts, 0), 1) < 50;

-- ============================================================================
-- QUERY 5: Composite Friction Score
-- Aggregates all friction types into a single member-level view
-- ============================================================================
WITH pa_friction AS (
    -- (Use Query 1 logic, simplified here for brevity)
    SELECT
        member_id,
        'PA_DELAY' AS friction_type,
        CASE
            WHEN AVG(DATEDIFF(day, auth_request_date, auth_approval_date)) > 14 THEN 3
            WHEN AVG(DATEDIFF(day, auth_request_date, auth_approval_date)) > 7 THEN 2
            ELSE 1
        END AS friction_score
    FROM authorizations
    WHERE auth_request_date >= DATEADD(month, -12, GETDATE())
    GROUP BY member_id
),
cost_friction AS (
    SELECT
        member_id,
        'COST_BARRIER' AS friction_type,
        CASE
            WHEN AVG(member_oop_cost) > 100 THEN 3
            WHEN AVG(member_oop_cost) > 50 THEN 2
            ELSE 1
        END AS friction_score
    FROM pharmacy_claims
    WHERE fill_date >= DATEADD(month, -12, GETDATE())
    GROUP BY member_id
),
outreach_friction AS (
    SELECT
        member_id,
        'OUTREACH_TIMING' AS friction_type,
        CASE
            WHEN SUM(CASE WHEN outcome IN ('NO_ANSWER', 'VOICEMAIL') THEN 1 ELSE 0 END) > 5 THEN 3
            WHEN SUM(CASE WHEN outcome IN ('NO_ANSWER', 'VOICEMAIL') THEN 1 ELSE 0 END) > 2 THEN 2
            ELSE 1
        END AS friction_score
    FROM outreach_log
    WHERE outreach_date >= DATEADD(month, -6, GETDATE())
    GROUP BY member_id
),
all_friction AS (
    SELECT * FROM pa_friction
    UNION ALL
    SELECT * FROM cost_friction
    UNION ALL
    SELECT * FROM outreach_friction
)
SELECT
    af.member_id,
    SUM(af.friction_score) AS total_friction_score,
    COUNT(DISTINCT af.friction_type) AS friction_types_present,
    STRING_AGG(af.friction_type, ', ') AS friction_categories,
    CASE
        WHEN SUM(af.friction_score) >= 7 THEN 'SYSTEM_FAILURE'
        WHEN SUM(af.friction_score) >= 5 THEN 'HIGH_FRICTION'
        WHEN SUM(af.friction_score) >= 3 THEN 'MODERATE_FRICTION'
        ELSE 'LOW_FRICTION'
    END AS friction_classification,
    'COMPOSITE' AS analysis_type
FROM all_friction af
GROUP BY af.member_id
ORDER BY SUM(af.friction_score) DESC;

-- ============================================================================
-- QUERY 6: Friction-Adjusted Nonadherence Flag
-- Reclassifies "nonadherent" members by distinguishing behavioral vs system causes
-- ============================================================================
WITH adherence_flags AS (
    SELECT
        cm.member_id,
        cm.care_gap_type,
        cm.date_identified,
        cm.status, -- 'OPEN', 'CLOSED', 'IN_PROGRESS'
        cm.days_open
    FROM care_management_gaps cm
    WHERE cm.date_identified >= DATEADD(month, -12, GETDATE())
      AND cm.status = 'OPEN'
),
system_friction AS (
    -- Combined friction from PA, cost, and outreach
    SELECT
        member_id,
        SUM(friction_score) AS system_friction_score
    FROM (
        SELECT member_id,
               CASE WHEN AVG(DATEDIFF(day, auth_request_date, auth_approval_date)) > 7 THEN 2 ELSE 0 END AS friction_score
        FROM authorizations
        WHERE auth_request_date >= DATEADD(month, -12, GETDATE())
        GROUP BY member_id
        UNION ALL
        SELECT member_id,
               CASE WHEN AVG(member_oop_cost) > 50 THEN 2 ELSE 0 END AS friction_score
        FROM pharmacy_claims
        WHERE fill_date >= DATEADD(month, -12, GETDATE())
        GROUP BY member_id
    ) combined
    GROUP BY member_id
)
SELECT
    af.member_id,
    af.care_gap_type,
    af.days_open,
    COALESCE(sf.system_friction_score, 0) AS system_friction_score,
    CASE
        WHEN COALESCE(sf.system_friction_score, 0) >= 3 THEN 'SYSTEM-CAUSED'
        WHEN COALESCE(sf.system_friction_score, 0) >= 1 THEN 'MIXED-CAUSE'
        ELSE 'BEHAVIORAL'
    END AS nonadherence_attribution,
    CASE
        WHEN COALESCE(sf.system_friction_score, 0) >= 3
        THEN 'Address PA delays, cost barriers, or access issues first'
        WHEN COALESCE(sf.system_friction_score, 0) >= 1
        THEN 'Reduce system friction before behavioral intervention'
        ELSE 'Appropriate for standard care management outreach'
    END AS recommended_action
FROM adherence_flags af
LEFT JOIN system_friction sf ON af.member_id = sf.member_id
ORDER BY sf.system_friction_score DESC;
