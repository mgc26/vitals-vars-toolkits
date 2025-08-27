-- Medication Adherence Gap Analysis for Avatar Intervention Targeting
-- Identifies patients with poor medication compliance who would benefit from avatar reminder programs
-- Focus on high-value medications where non-adherence has significant clinical/financial impact

WITH medication_fills AS (
    SELECT 
        patient_id,
        medication_name,
        medication_class,
        ndc_code,
        fill_date,
        days_supply,
        refills_remaining,
        prescriber_id,
        -- Calculate when medication should run out
        fill_date + INTERVAL '1 day' * days_supply AS expected_refill_date,
        -- Get next fill date for same medication
        LEAD(fill_date) OVER (PARTITION BY patient_id, medication_name ORDER BY fill_date) AS next_fill_date
    FROM pharmacy_claims
    WHERE fill_date >= CURRENT_DATE - INTERVAL '12 months'
        AND days_supply > 0
),

adherence_metrics AS (
    SELECT 
        patient_id,
        medication_name,
        medication_class,
        COUNT(*) AS fill_count,
        
        -- Calculate Proportion of Days Covered (PDC)
        SUM(days_supply) AS total_days_supply,
        DATEDIFF('day', MIN(fill_date), CURRENT_DATE) AS days_in_period,
        LEAST(SUM(days_supply) * 1.0 / NULLIF(DATEDIFF('day', MIN(fill_date), CURRENT_DATE), 0), 1.0) AS pdc,
        
        -- Gap analysis
        AVG(CASE 
            WHEN next_fill_date IS NOT NULL 
            THEN DATEDIFF('day', expected_refill_date, next_fill_date)
            ELSE NULL 
        END) AS avg_gap_days,
        
        MAX(CASE 
            WHEN next_fill_date IS NOT NULL 
            THEN DATEDIFF('day', expected_refill_date, next_fill_date)
            ELSE DATEDIFF('day', expected_refill_date, CURRENT_DATE)
        END) AS max_gap_days,
        
        -- Late refill patterns
        SUM(CASE 
            WHEN next_fill_date > expected_refill_date + INTERVAL '7 days' 
            THEN 1 
            ELSE 0 
        END) AS late_refills,
        
        -- Current status
        MAX(fill_date) AS last_fill_date,
        MAX(expected_refill_date) AS last_expected_refill_date,
        MAX(refills_remaining) AS current_refills_remaining
        
    FROM medication_fills
    GROUP BY patient_id, medication_name, medication_class
),

high_value_medications AS (
    -- Define medications where non-adherence has highest impact
    SELECT medication_class, priority_score, annual_cost_nonadherence, clinical_risk
    FROM (VALUES
        ('Anticoagulants', 10, 15000, 'Stroke/PE Risk'),
        ('Insulin', 9, 8000, 'DKA/Complications'),
        ('Heart Failure', 9, 12000, 'Decompensation'),
        ('Antipsychotics', 8, 20000, 'Psychiatric Admission'),
        ('HIV Antiretrovirals', 8, 25000, 'Viral Resistance'),
        ('Immunosuppressants', 8, 30000, 'Transplant Rejection'),
        ('Statins', 7, 5000, 'CV Events'),
        ('Antihypertensives', 7, 6000, 'Stroke/MI'),
        ('Oral Diabetes', 6, 4000, 'Poor Glycemic Control'),
        ('Asthma Controllers', 6, 3500, 'Exacerbations')
    ) AS t(medication_class, priority_score, annual_cost_nonadherence, clinical_risk)
),

patient_risk AS (
    SELECT 
        p.patient_id,
        p.age,
        -- Count chronic conditions requiring medication
        SUM(CASE WHEN d.icd10_code LIKE 'E11%' THEN 1 ELSE 0 END) AS has_diabetes,
        SUM(CASE WHEN d.icd10_code LIKE 'I10%' THEN 1 ELSE 0 END) AS has_hypertension,
        SUM(CASE WHEN d.icd10_code LIKE 'I50%' THEN 1 ELSE 0 END) AS has_chf,
        SUM(CASE WHEN d.icd10_code IN ('I48.0', 'I48.1', 'I48.2') THEN 1 ELSE 0 END) AS has_afib,
        -- Healthcare utilization as proxy for complexity
        COUNT(DISTINCT e.encounter_id) AS admissions_12mo,
        COUNT(DISTINCT ed.encounter_id) AS ed_visits_12mo
    FROM patients p
    LEFT JOIN diagnoses d ON p.patient_id = d.patient_id
    LEFT JOIN encounters e ON p.patient_id = e.patient_id 
        AND e.admission_date >= CURRENT_DATE - INTERVAL '12 months'
    LEFT JOIN emergency_visits ed ON p.patient_id = ed.patient_id
        AND ed.arrival_date >= CURRENT_DATE - INTERVAL '12 months'
    GROUP BY p.patient_id, p.age
),

adherence_gaps AS (
    SELECT 
        am.patient_id,
        am.medication_name,
        am.medication_class,
        am.pdc,
        am.avg_gap_days,
        am.max_gap_days,
        am.late_refills,
        am.fill_count,
        am.last_fill_date,
        am.last_expected_refill_date,
        am.current_refills_remaining,
        
        pr.age,
        pr.admissions_12mo,
        pr.ed_visits_12mo,
        
        hvm.priority_score,
        hvm.annual_cost_nonadherence,
        hvm.clinical_risk,
        
        -- Calculate non-adherence impact score
        (1 - am.pdc) * hvm.priority_score * 10 AS nonadherence_impact_score,
        
        -- Estimate annual cost of non-adherence for this patient
        (1 - am.pdc) * hvm.annual_cost_nonadherence AS estimated_annual_cost,
        
        -- Days overdue for current refill
        CASE 
            WHEN am.last_expected_refill_date < CURRENT_DATE 
            THEN DATEDIFF('day', am.last_expected_refill_date, CURRENT_DATE)
            ELSE 0
        END AS days_overdue
        
    FROM adherence_metrics am
    INNER JOIN high_value_medications hvm ON am.medication_class = hvm.medication_class
    LEFT JOIN patient_risk pr ON am.patient_id = pr.patient_id
    WHERE am.pdc < 0.8  -- Standard adherence threshold
)

-- Final targeting list for avatar intervention
SELECT 
    patient_id,
    medication_name,
    medication_class,
    clinical_risk,
    
    ROUND(pdc * 100, 1) AS adherence_percentage,
    avg_gap_days,
    max_gap_days,
    late_refills,
    days_overdue,
    
    -- Intervention urgency
    CASE 
        WHEN days_overdue > 14 AND priority_score >= 8 THEN 'URGENT - Immediate Outreach'
        WHEN days_overdue > 7 AND priority_score >= 7 THEN 'High Priority - Contact Today'
        WHEN pdc < 0.5 AND priority_score >= 7 THEN 'High Risk - Intensive Support Needed'
        WHEN late_refills >= 3 THEN 'Pattern Non-Adherent - Behavior Modification'
        ELSE 'Standard Reminder Program'
    END AS intervention_priority,
    
    -- Avatar program recommendation
    CASE 
        WHEN medication_class IN ('Insulin', 'Anticoagulants') THEN 'Daily Check-in Avatar'
        WHEN late_refills >= 3 THEN 'Behavioral Coaching Avatar'
        WHEN avg_gap_days > 7 THEN 'Refill Reminder Avatar'
        WHEN age >= 75 THEN 'Senior Support Avatar'
        ELSE 'Standard Reminder Avatar'
    END AS avatar_program_type,
    
    -- Estimated ROI of intervention
    ROUND(estimated_annual_cost * 0.3, 0) AS potential_savings_30pct_improvement,
    
    -- Engagement frequency recommendation
    CASE 
        WHEN priority_score >= 9 THEN 'Daily'
        WHEN priority_score >= 7 OR pdc < 0.5 THEN 'Every 3 Days'
        WHEN pdc < 0.7 THEN 'Weekly'
        ELSE 'Bi-weekly'
    END AS recommended_contact_frequency,
    
    -- Content focus areas
    CONCAT_WS(', ',
        CASE WHEN days_overdue > 0 THEN 'Immediate Refill Needed' END,
        CASE WHEN current_refills_remaining = 0 THEN 'Provider Appointment Required' END,
        CASE WHEN avg_gap_days > 7 THEN 'Refill Timing Education' END,
        CASE WHEN medication_class = 'Insulin' THEN 'Injection Technique Support' END,
        CASE WHEN medication_class = 'Asthma Controllers' THEN 'Inhaler Technique Review' END,
        CASE WHEN age >= 75 THEN 'Simplified Regimen Discussion' END,
        CASE WHEN admissions_12mo > 0 THEN 'Importance for Staying Healthy' END
    ) AS avatar_content_priorities,
    
    nonadherence_impact_score,
    estimated_annual_cost AS annual_cost_of_nonadherence

FROM adherence_gaps
WHERE nonadherence_impact_score > 10  -- Focus on highest impact opportunities
    OR days_overdue > 7  -- Or currently overdue medications

ORDER BY 
    nonadherence_impact_score DESC,
    days_overdue DESC,
    priority_score DESC

LIMIT 500;  -- Top candidates for pilot program