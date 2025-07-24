-- Denial Hotspot Analysis for Prior Authorization
-- Purpose: Identify highest-impact denial areas for immediate focus
-- Compatible with: Most SQL databases (adjust date functions as needed)

-- ============================================
-- 1. TOP 5 PAYERS BY DENIED REVENUE
-- ============================================
-- Shows which payers are causing the most financial impact
SELECT 
    p.payer_name,
    COUNT(c.claim_id) AS total_claims,
    SUM(CASE WHEN c.claim_status = 'denied' THEN 1 ELSE 0 END) AS denied_claims,
    ROUND(100.0 * SUM(CASE WHEN c.claim_status = 'denied' THEN 1 ELSE 0 END) / COUNT(c.claim_id), 2) AS denial_rate_pct,
    SUM(CASE WHEN c.claim_status = 'denied' THEN c.claim_value ELSE 0 END) AS total_denied_value,
    SUM(CASE WHEN c.claim_status = 'denied' AND c.denial_reason LIKE '%auth%' THEN c.claim_value ELSE 0 END) AS pa_denied_value
FROM 
    claims c
    INNER JOIN payers p ON c.payer_id = p.payer_id
WHERE 
    c.claim_date >= DATEADD(month, -6, GETDATE())  -- Last 6 months
    -- For PostgreSQL: c.claim_date >= CURRENT_DATE - INTERVAL '6 months'
    -- For MySQL: c.claim_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
GROUP BY 
    p.payer_name
ORDER BY 
    pa_denied_value DESC
LIMIT 5;

-- ============================================
-- 2. TOP 10 DENIED PROCEDURES (CPT CODES)
-- ============================================
-- Identifies which procedures need documentation improvement
SELECT 
    cpt.cpt_code,
    cpt.procedure_description,
    COUNT(c.claim_id) AS total_claims,
    SUM(CASE WHEN c.claim_status = 'denied' AND c.denial_reason LIKE '%auth%' THEN 1 ELSE 0 END) AS pa_denials,
    ROUND(100.0 * SUM(CASE WHEN c.claim_status = 'denied' AND c.denial_reason LIKE '%auth%' THEN 1 ELSE 0 END) / COUNT(c.claim_id), 2) AS pa_denial_rate,
    SUM(CASE WHEN c.claim_status = 'denied' AND c.denial_reason LIKE '%auth%' THEN c.claim_value ELSE 0 END) AS pa_denied_value,
    AVG(CASE WHEN c.claim_status = 'denied' AND c.denial_reason LIKE '%auth%' THEN c.claim_value ELSE NULL END) AS avg_denial_value
FROM 
    claims c
    INNER JOIN cpt_codes cpt ON c.cpt_code = cpt.cpt_code
WHERE 
    c.claim_date >= DATEADD(month, -6, GETDATE())
GROUP BY 
    cpt.cpt_code, cpt.procedure_description
HAVING 
    COUNT(c.claim_id) >= 10  -- Filter out low-volume procedures
ORDER BY 
    pa_denied_value DESC
LIMIT 10;

-- ============================================
-- 3. DENIAL REASONS BREAKDOWN
-- ============================================
-- Understand why claims are being denied
SELECT 
    dr.denial_reason_category,
    dr.denial_reason_description,
    COUNT(c.claim_id) AS denial_count,
    SUM(c.claim_value) AS total_denied_value,
    ROUND(AVG(c.claim_value), 2) AS avg_denial_value
FROM 
    claims c
    INNER JOIN denial_reasons dr ON c.denial_reason_code = dr.denial_reason_code
WHERE 
    c.claim_status = 'denied'
    AND c.denial_reason LIKE '%auth%'
    AND c.claim_date >= DATEADD(month, -3, GETDATE())
GROUP BY 
    dr.denial_reason_category, dr.denial_reason_description
ORDER BY 
    denial_count DESC
LIMIT 20;

-- ============================================
-- 4. SERVICE LINE PERFORMANCE
-- ============================================
-- Compare denial rates across departments
SELECT 
    d.department_name,
    d.service_line,
    COUNT(c.claim_id) AS total_claims,
    SUM(CASE WHEN c.claim_status = 'denied' AND c.denial_reason LIKE '%auth%' THEN 1 ELSE 0 END) AS pa_denials,
    ROUND(100.0 * SUM(CASE WHEN c.claim_status = 'denied' AND c.denial_reason LIKE '%auth%' THEN 1 ELSE 0 END) / COUNT(c.claim_id), 2) AS pa_denial_rate,
    SUM(c.claim_value) AS total_claim_value,
    SUM(CASE WHEN c.claim_status = 'denied' AND c.denial_reason LIKE '%auth%' THEN c.claim_value ELSE 0 END) AS pa_denied_value,
    ROUND(100.0 * SUM(CASE WHEN c.claim_status = 'denied' AND c.denial_reason LIKE '%auth%' THEN c.claim_value ELSE 0 END) / SUM(c.claim_value), 2) AS denied_value_pct
FROM 
    claims c
    INNER JOIN departments d ON c.department_id = d.department_id
WHERE 
    c.claim_date >= DATEADD(month, -3, GETDATE())
GROUP BY 
    d.department_name, d.service_line
ORDER BY 
    pa_denied_value DESC;

-- ============================================
-- 5. TREND ANALYSIS - MONTHLY DENIAL RATES
-- ============================================
-- Track improvement over time
SELECT 
    YEAR(c.claim_date) AS claim_year,
    MONTH(c.claim_date) AS claim_month,
    COUNT(c.claim_id) AS total_claims,
    SUM(CASE WHEN c.claim_status = 'denied' THEN 1 ELSE 0 END) AS total_denials,
    SUM(CASE WHEN c.claim_status = 'denied' AND c.denial_reason LIKE '%auth%' THEN 1 ELSE 0 END) AS pa_denials,
    ROUND(100.0 * SUM(CASE WHEN c.claim_status = 'denied' AND c.denial_reason LIKE '%auth%' THEN 1 ELSE 0 END) / COUNT(c.claim_id), 2) AS pa_denial_rate,
    SUM(c.claim_value) AS total_claim_value,
    SUM(CASE WHEN c.claim_status = 'denied' AND c.denial_reason LIKE '%auth%' THEN c.claim_value ELSE 0 END) AS pa_denied_value
FROM 
    claims c
WHERE 
    c.claim_date >= DATEADD(year, -1, GETDATE())
GROUP BY 
    YEAR(c.claim_date), MONTH(c.claim_date)
ORDER BY 
    claim_year DESC, claim_month DESC;