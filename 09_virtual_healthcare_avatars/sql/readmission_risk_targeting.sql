-- Readmission Risk Targeting for Avatar Interventions
-- Identifies high-risk patients who would benefit most from virtual avatar discharge education
-- Target: Patients with >20% readmission risk based on historical patterns

WITH readmission_history AS (
    SELECT 
        patient_id,
        admission_date,
        discharge_date,
        principal_diagnosis_code,
        drg_code,
        discharge_disposition,
        length_of_stay,
        -- Flag readmissions within 30 days
        CASE 
            WHEN LEAD(admission_date) OVER (PARTITION BY patient_id ORDER BY admission_date) 
                 <= discharge_date + INTERVAL '30 days' 
            THEN 1 
            ELSE 0 
        END AS readmitted_30_day
    FROM encounters
    WHERE discharge_date >= CURRENT_DATE - INTERVAL '2 years'
        AND discharge_date < CURRENT_DATE - INTERVAL '30 days'  -- Ensure we can measure 30-day outcome
        AND discharge_disposition NOT IN ('Expired', 'Hospice', 'AMA')
),

risk_factors AS (
    SELECT 
        e.patient_id,
        e.encounter_id,
        e.admission_date,
        e.principal_diagnosis_code,
        e.drg_code,
        
        -- Clinical risk factors
        p.age,
        CASE WHEN p.age >= 65 THEN 1 ELSE 0 END AS elderly,
        
        -- Comorbidity burden (Charlson components)
        MAX(CASE WHEN d.icd10_code LIKE 'E11%' THEN 1 ELSE 0 END) AS has_diabetes,
        MAX(CASE WHEN d.icd10_code LIKE 'I50%' THEN 1 ELSE 0 END) AS has_chf,
        MAX(CASE WHEN d.icd10_code LIKE 'J44%' THEN 1 ELSE 0 END) AS has_copd,
        MAX(CASE WHEN d.icd10_code LIKE 'N18%' THEN 1 ELSE 0 END) AS has_ckd,
        
        -- Healthcare utilization
        COUNT(DISTINCT e2.encounter_id) AS prior_admissions_12mo,
        COUNT(DISTINCT ed.encounter_id) AS ed_visits_6mo,
        
        -- Social determinants
        CASE WHEN p.insurance_type IN ('Medicaid', 'Self-Pay') THEN 1 ELSE 0 END AS vulnerable_insurance,
        CASE WHEN p.preferred_language != 'English' THEN 1 ELSE 0 END AS language_barrier,
        
        -- Medication complexity
        COUNT(DISTINCT m.medication_name) AS medication_count,
        MAX(CASE WHEN m.high_risk_flag = 1 THEN 1 ELSE 0 END) AS on_high_risk_meds
        
    FROM encounters e
    INNER JOIN patients p ON e.patient_id = p.patient_id
    LEFT JOIN diagnoses d ON e.encounter_id = d.encounter_id
    LEFT JOIN encounters e2 ON p.patient_id = e2.patient_id 
        AND e2.admission_date BETWEEN e.admission_date - INTERVAL '12 months' AND e.admission_date - INTERVAL '1 day'
    LEFT JOIN emergency_visits ed ON p.patient_id = ed.patient_id
        AND ed.arrival_date BETWEEN e.admission_date - INTERVAL '6 months' AND e.admission_date
    LEFT JOIN medications m ON e.encounter_id = m.encounter_id
    
    WHERE e.discharge_date >= CURRENT_DATE - INTERVAL '30 days'
        AND e.discharge_date <= CURRENT_DATE
        AND e.discharge_disposition IN ('Home', 'Home Health', 'SNF')
    
    GROUP BY 
        e.patient_id, e.encounter_id, e.admission_date, 
        e.principal_diagnosis_code, e.drg_code, p.age,
        p.insurance_type, p.preferred_language
),

risk_scores AS (
    SELECT 
        *,
        -- Calculate composite risk score based on evidence
        (elderly * 2) +
        (has_diabetes * 1) +
        (has_chf * 3) +
        (has_copd * 2) +
        (has_ckd * 2) +
        (CASE 
            WHEN prior_admissions_12mo >= 3 THEN 3
            WHEN prior_admissions_12mo >= 1 THEN 2
            ELSE 0
        END) +
        (CASE 
            WHEN ed_visits_6mo >= 2 THEN 2
            WHEN ed_visits_6mo >= 1 THEN 1
            ELSE 0
        END) +
        (vulnerable_insurance * 1) +
        (language_barrier * 1) +
        (CASE 
            WHEN medication_count >= 10 THEN 2
            WHEN medication_count >= 5 THEN 1
            ELSE 0
        END) +
        (on_high_risk_meds * 2) AS total_risk_score
    FROM risk_factors
),

historical_rates AS (
    SELECT 
        drg_code,
        principal_diagnosis_code,
        AVG(readmitted_30_day) AS baseline_readmission_rate,
        COUNT(*) AS sample_size
    FROM readmission_history
    GROUP BY drg_code, principal_diagnosis_code
    HAVING COUNT(*) >= 30  -- Minimum sample for reliable estimate
)

-- Final patient targeting list
SELECT 
    rs.patient_id,
    rs.encounter_id,
    rs.admission_date,
    rs.drg_code,
    rs.principal_diagnosis_code,
    rs.age,
    rs.total_risk_score,
    
    -- Risk categorization
    CASE 
        WHEN rs.total_risk_score >= 10 THEN 'Very High'
        WHEN rs.total_risk_score >= 7 THEN 'High'
        WHEN rs.total_risk_score >= 4 THEN 'Moderate'
        ELSE 'Low'
    END AS risk_category,
    
    -- Historical baseline for this condition
    hr.baseline_readmission_rate,
    
    -- Estimated readmission probability
    CASE 
        WHEN rs.total_risk_score >= 10 THEN LEAST(hr.baseline_readmission_rate * 2.5, 0.8)
        WHEN rs.total_risk_score >= 7 THEN LEAST(hr.baseline_readmission_rate * 1.8, 0.6)
        WHEN rs.total_risk_score >= 4 THEN LEAST(hr.baseline_readmission_rate * 1.3, 0.4)
        ELSE hr.baseline_readmission_rate
    END AS estimated_readmission_probability,
    
    -- Avatar intervention recommendation
    CASE 
        WHEN rs.total_risk_score >= 7 
            AND hr.baseline_readmission_rate >= 0.15 
            THEN 'High Priority - Immediate Avatar Intervention'
        WHEN rs.total_risk_score >= 4 
            AND hr.baseline_readmission_rate >= 0.10 
            THEN 'Medium Priority - Schedule Within 24 Hours'
        WHEN rs.language_barrier = 1 
            THEN 'Consider Multilingual Avatar Support'
        ELSE 'Standard Discharge Process'
    END AS avatar_recommendation,
    
    -- Specific focus areas for avatar interaction
    CONCAT_WS(', ',
        CASE WHEN rs.medication_count >= 10 THEN 'Medication Management Focus' END,
        CASE WHEN rs.has_chf = 1 THEN 'Daily Weight Monitoring' END,
        CASE WHEN rs.has_copd = 1 THEN 'Inhaler Technique Review' END,
        CASE WHEN rs.has_diabetes = 1 THEN 'Glucose Monitoring Education' END,
        CASE WHEN rs.ed_visits_6mo >= 2 THEN 'Warning Sign Recognition' END,
        CASE WHEN rs.vulnerable_insurance = 1 THEN 'Resource Navigation' END
    ) AS avatar_content_priorities

FROM risk_scores rs
LEFT JOIN historical_rates hr 
    ON rs.drg_code = hr.drg_code 
    AND rs.principal_diagnosis_code = hr.principal_diagnosis_code

WHERE rs.total_risk_score >= 4  -- Focus on moderate to high risk
    OR hr.baseline_readmission_rate >= 0.15  -- Or historically problematic conditions

ORDER BY 
    rs.total_risk_score DESC,
    hr.baseline_readmission_rate DESC,
    rs.admission_date DESC;